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
   Entities.clear_pending_actions(world, entity)
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
   schedule_action(world, miner, miner.create_miner_action(world, i_store),
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

