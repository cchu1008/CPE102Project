import entities
import worldmodel
import pygame
import math
import random
import point
import image_store

BLOB_RATE_SCALE = 4
BLOB_ANIMATION_RATE_SCALE = 50
BLOB_ANIMATION_MIN = 1
BLOB_ANIMATION_MAX = 3

ORE_CORRUPT_MIN = 20000
ORE_CORRUPT_MAX = 30000

QUAKE_STEPS = 10
QUAKE_DURATION = 1100
QUAKE_ANIMATION_RATE = 100

VEIN_SPAWN_DELAY = 500
VEIN_RATE_MIN = 8000
VEIN_RATE_MAX = 17000


def sign(x):
   if x < 0:
      return -1
   elif x > 0:
      return 1
   else:
      return 0

def next_position(world, entity_pt, dest_pt):
   horiz = sign(dest_pt.x - entity_pt.x)
   new_pt = point.Point(entity_pt.x + horiz, entity_pt.y)

   if horiz == 0 or world.is_occupied(new_pt):
      vert = sign(dest_pt.y - entity_pt.y)
      new_pt = point.Point(entity_pt.x, entity_pt.y + vert)

      if vert == 0 or world.is_occupied(new_pt):
         new_pt = point.Point(entity_pt.x, entity_pt.y)

   return new_pt


def find_open_around(world, pt, distance):
   for dy in range(-distance, distance + 1):
      for dx in range(-distance, distance + 1):
         new_pt = point.Point(pt.x + dx, pt.y + dy)

         if (world.within_bounds(new_pt) and
            (not world.is_occupied(new_pt))):
            return new_pt

   return None


def try_transform_miner(world, entity, transform):
   new_entity = transform(world, entity)
   if entity != new_entity:
      clear_pending_actions(world, entity)
      world.remove_entity_at(entities.get_position(entity))
      world.add_entity(new_entity)
      schedule_animation(world, new_entity)

   return new_entity


def create_miner_action(world, entity, image_store):
   if isinstance(entity, entities.MinerNotFull):
      return entity.create_miner_not_full_action(world, image_store)
   else:
      return entity.create_miner_full_action(world, image_store)


def create_animation_action(world, entity, repeat_count):
   def action(current_ticks):
      entities.remove_pending_action(entity, action)

      entities.next_image(entity)

      if repeat_count != 1:
         schedule_action(world, entity,
            create_animation_action(world, entity, max(repeat_count - 1, 0)),
            current_ticks + entities.get_animation_rate(entity))

      return [entities.get_position(entity)]
   return action


def create_entity_death_action(world, entity):
   def action(current_ticks):
      entities.remove_pending_action(entity, action)
      pt = entities.get_position(entity)
      remove_entity(world, entity)
      return [pt]
   return action


def create_ore_transform_action(world, entity, i_store):
   def action(current_ticks):
      entities.remove_pending_action(entity, action)
      blob = create_blob(world, entities.get_name(entity) + " -- blob",
         entities.get_position(entity),
         entities.get_rate(entity) // BLOB_RATE_SCALE,
         current_ticks, i_store)

      remove_entity(world, entity)
      world.add_entity(blob)

      return [entities.get_position(blob)]
   return action


def remove_entity(world, entity):
   for action in entities.get_pending_actions(entity):
      world.unschedule_action(action)
   entities.clear_pending_actions(entity)
   world.remove_entity(entity)


def create_blob(world, name, pt, rate, ticks, i_store):
   blob = entities.OreBlob(name, pt, rate,
      image_store.get_images(i_store, 'blob'),
      random.randint(BLOB_ANIMATION_MIN, BLOB_ANIMATION_MAX)
      * BLOB_ANIMATION_RATE_SCALE)
   schedule_blob(world, blob, ticks, i_store)
   return blob


def schedule_blob(world, blob, ticks, i_store):
   schedule_action(world, blob, blob.create_ore_blob_action(world, i_store),
      ticks + entities.get_rate(blob))
   schedule_animation(world, blob)


def schedule_miner(world, miner, ticks, i_store):
   schedule_action(world, miner, create_miner_action(world, miner, i_store),
      ticks + entities.get_rate(miner))
   schedule_animation(world, miner)


def create_ore(world, name, pt, ticks, i_store):
   ore = entities.Ore(name, pt, image_store.get_images(i_store, 'ore'),
      random.randint(ORE_CORRUPT_MIN, ORE_CORRUPT_MAX))
   schedule_ore(world, ore, ticks, i_store)

   return ore


def schedule_ore(world, ore, ticks, i_store):
   schedule_action(world, ore,
      create_ore_transform_action(world, ore, i_store),
      ticks + entities.get_rate(ore))


def create_quake(world, pt, ticks, i_store):
   quake = entities.Quake("quake", pt,
      image_store.get_images(i_store, 'quake'), QUAKE_ANIMATION_RATE)
   schedule_quake(world, quake, ticks)
   return quake


def schedule_quake(world, quake, ticks):
   schedule_animation(world, quake, QUAKE_STEPS) 
   schedule_action(world, quake, create_entity_death_action(world, quake),
      ticks + QUAKE_DURATION)


def create_vein(world, name, pt, ticks, i_store):
   vein = entities.Vein("vein" + name,
      random.randint(VEIN_RATE_MIN, VEIN_RATE_MAX),
      pt, image_store.get_images(i_store, 'vein'))
   return vein


def schedule_vein(world, vein, ticks, i_store):
   schedule_action(world, vein, vein.create_vein_action(world, i_store),
      ticks + entities.get_rate(vein))


def schedule_action(world, entity, action, time):
   entities.add_pending_action(entity, action)
   world.schedule_action(action, time)


def schedule_animation(world, entity, repeat_count=0):
   schedule_action(world, entity,
      create_animation_action(world, entity, repeat_count),
      entities.get_animation_rate(entity))


def clear_pending_actions(world, entity):
   for action in entities.get_pending_actions(entity):
      world.unschedule_action(action)
   entities.clear_pending_actions(entity)
