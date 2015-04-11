import point
import actions

class Background:
   def __init__(self, name, imgs):
      self.name = name
      self.imgs = imgs
      self.current_img = 0
      
   def get_name(self):
      return self.name
      
   def get_images(self):
      return self.imgs

   def get_image(self):
      return self.imgs[self.current_img]
      
   def next_image(self):
      self.current_img = (self.current_img + 1) % len(self.imgs)

   def entity_string(self):
      return 'unknown'

class MinerNotFull:
   def __init__(self, name, resource_limit, position, rate, imgs,
      animation_rate):
      self.name = name
      self.position = position
      self.rate = rate
      self.imgs = imgs
      self.current_img = 0
      self.resource_limit = resource_limit
      self.resource_count = 0
      self.animation_rate = animation_rate
      self.pending_actions = []
      
   def get_name(self):
      return self.name
      
   def set_position(self, point):
      self.position = point

   def get_position(self):
      return self.position

   def get_rate(self):
      return self.rate
      
   def get_images(self):
      return self.imgs

   def get_image(self):
      return self.imgs[self.current_img]
      
   def next_image(self):
      self.current_img = (self.current_img + 1) % len(self.imgs)

   def get_animation_rate(self):
      return self.animation_rate
      
   def get_resource_count(self):
      return self.resource_count

   def set_resource_count(self, n):
      self.resource_count = n
      
   def get_resource_limit(self):
      return self.resource_limit
      
   def remove_pending_action(self, action):
      self.pending_actions.remove(action)

   def add_pending_action(self, action):
      self.pending_actions.append(action)


   def get_pending_actions(self):
      return self.pending_actions

   def clear_entity_pending_actions(self):
      self.pending_actions = []

   def clear_pending_actions(self, world):
      for action in self.get_pending_actions():
         world.unschedule_action(action)
      self.clear_entity_pending_actions()

   def entity_string(self):
      return ' '.join(['miner', self.name, str(self.position.x),
         str(self.position.y), str(self.resource_limit),
         str(self.rate), str(self.animation_rate)])
         
   def miner_to_ore(self, world, ore):
      entity_pt = self.position
      if not ore:
         return ([entity_pt], False)
      ore_pt = ore.get_position()
      if adjacent(entity_pt, ore_pt):
         self.set_resource_count(1 + self.resource_count)
         actions.remove_entity(world, ore)
         return ([ore_pt], True)
      else:
         new_pt = next_position(world, entity_pt, ore_pt)
         return (world.move_entity(self, new_pt), False)
         
   def create_miner_not_full_action(self, world, i_store):
      def action(current_ticks):
         self.remove_pending_action(action)

         entity_pt = self.position
         ore = world.find_nearest(entity_pt, Ore)
         (tiles, found) = self.miner_to_ore(world, ore)

         new_entity = self
         if found:
            new_entity = try_transform_miner(world, self,
               try_transform_miner_not_full)

         actions.schedule_action(world, new_entity,
            new_entity.create_miner_action(world, i_store),
            current_ticks + new_entity.get_rate())
         return tiles
      return action
      
   def create_miner_action(self, world, image_store):
      return self.create_miner_not_full_action(world, image_store)

      
class MinerFull:
   def __init__(self, name, resource_limit, position, rate, imgs,
      animation_rate):
      self.name = name
      self.position = position
      self.rate = rate
      self.imgs = imgs
      self.current_img = 0
      self.resource_limit = resource_limit
      self.resource_count = resource_limit
      self.animation_rate = animation_rate
      self.pending_actions = []
      
   def get_name(self):
      return self.name
      
   def set_position(self, point):
      self.position = point

   def get_position(self):
      return self.position

   def get_rate(self):
      return self.rate
      
   def get_images(self):
      return self.imgs

   def get_image(self):
      return self.imgs[self.current_img]
      
   def next_image(self):
      self.current_img = (self.current_img + 1) % len(self.imgs)

   def get_animation_rate(self):
      return self.animation_rate
      
   def get_resource_count(self):
      return self.resource_count

   def set_resource_count(self, n):
      self.resource_count = n
      
   def get_resource_limit(self):
      return self.resource_limit
      
   def remove_pending_action(self, action):
      self.pending_actions.remove(action)

   def add_pending_action(self, action):
      self.pending_actions.append(action)


   def get_pending_actions(self):
      return self.pending_actions

   def clear_entity_pending_actions(self):
      self.pending_actions = []

   def clear_pending_actions(self, world):
      for action in self.get_pending_actions():
         world.unschedule_action(action)
      self.clear_entity_pending_actions()

   def entity_string(self):
      return 'unknown'
      
   def miner_to_smith(self, world, smith):
      entity_pt = self.position
      if not smith:
         return ([entity_pt], False)
      smith_pt = smith.get_position()
      if adjacent(entity_pt, smith_pt):
         smith.set_resource_count( 
            smith.get_resource_count() +
            self.resource_count)
         self.resource_count = 0
         return ([], True)
      else:
         new_pt = next_position(world, entity_pt, smith_pt)
         return (world.move_entity(self, new_pt), False)
         
   def create_miner_full_action(self, world, i_store):
      def action(current_ticks):
         self.remove_pending_action(action)

         entity_pt = self.position
         smith = world.find_nearest(entity_pt, Blacksmith)
         (tiles, found) = self.miner_to_smith(world, smith)

         new_entity = self
         if found:
            new_entity = try_transform_miner(world, self,
               try_transform_miner_full)

         actions.schedule_action(world, new_entity,
            new_entity.create_miner_action(world, i_store),
            current_ticks + new_entity.get_rate())
         return tiles
      return action
      
   def create_miner_action(self, world, image_store):
      return self.create_miner_full_action(world, image_store)


class Vein:
   def __init__(self, name, rate, position, imgs, resource_distance=1):
      self.name = name
      self.position = position
      self.rate = rate
      self.imgs = imgs
      self.current_img = 0
      self.resource_distance = resource_distance
      self.pending_actions = []
      
   def get_name(self):
      return self.name
      
   def set_position(self, point):
      self.position = point

   def get_position(self):
      return self.position

   def get_rate(self):
      return self.rate
      
   def get_images(self):
      return self.imgs

   def get_image(self):
      return self.imgs[self.current_img]
      
   def next_image(self):
      self.current_img = (self.current_img + 1) % len(self.imgs)

   def get_resource_distance(self):
      return self.resource_distance
      
   def remove_pending_action(self, action):
      self.pending_actions.remove(action)

   def add_pending_action(self, action):
      self.pending_actions.append(action)


   def get_pending_actions(self):
      return self.pending_actions

   def clear_entity_pending_actions(self):
      self.pending_actions = []

   def clear_pending_actions(self, world):
      for action in self.get_pending_actions():
         world.unschedule_action(action)
      self.clear_entity_pending_actions()

   def entity_string(self):
      return ' '.join(['vein', self.name, str(self.position.x),
         str(self.position.y), str(self.rate),
         str(self.resource_distance)])
         
   def create_vein_action(self, world, i_store):
      def action(current_ticks):
         self.remove_pending_action(action)

         open_pt = find_open_around(world, self.position,
            self.resource_distance)
         if open_pt:
            ore = actions.create_ore(world,
               "ore - " + self.name + " - " + str(current_ticks),
               open_pt, current_ticks, i_store)
            world.add_entity(ore)
            tiles = [open_pt]
         else:
            tiles = []

         actions.schedule_action(world, self,
            self.create_vein_action(world, i_store),
            current_ticks + self.rate)
         return tiles
      return action
      
class Ore:
   def __init__(self, name, position, imgs, rate=5000):
      self.name = name
      self.position = position
      self.imgs = imgs
      self.current_img = 0
      self.rate = rate
      self.pending_actions = []
      
   def get_name(self):
      return self.name
      
   def set_position(self, point):
      self.position = point

   def get_position(self):
      return self.position

   def get_rate(self):
      return self.rate
      
   def get_images(self):
      return self.imgs

   def get_image(self):
      return self.imgs[self.current_img]
      
   def next_image(self):
      self.current_img = (self.current_img + 1) % len(self.imgs)

   def remove_pending_action(self, action):
      self.pending_actions.remove(action)

   def add_pending_action(self, action):
      self.pending_actions.append(action)


   def get_pending_actions(self):
      return self.pending_actions

   def clear_entity_pending_actions(self):
      self.pending_actions = []

   def clear_pending_actions(self, world):
      for action in self.get_pending_actions():
         world.unschedule_action(action)
      self.clear_entity_pending_actions()

   def entity_string(self):
      return ' '.join(['ore', self.name, str(self.position.x),
         str(self.position.y), str(self.rate)])
      
class Blacksmith:
   def __init__(self, name, position, imgs, resource_limit, rate,
      resource_distance=1):
      self.name = name
      self.position = position
      self.imgs = imgs
      self.current_img = 0
      self.resource_limit = resource_limit
      self.resource_count = 0
      self.rate = rate
      self.resource_distance = resource_distance
      self.pending_actions = []
      
   def get_name(self):
      return self.name
      
   def set_position(self, point):
      self.position = point

   def get_position(self):
      return self.position

   def get_rate(self):
      return self.rate
      
   def get_images(self):
      return self.imgs

   def get_image(self):
      return self.imgs[self.current_img]
      
   def next_image(self):
      self.current_img = (self.current_img + 1) % len(self.imgs)

   def get_resource_distance(self):
      return self.resource_distance
      
   def get_resource_count(self):
      return self.resource_count

   def set_resource_count(self, n):
      self.resource_count = n
      
   def get_resource_limit(self):
      return self.resource_limit
      
   def remove_pending_action(self, action):
      self.pending_actions.remove(action)

   def add_pending_action(self, action):
      self.pending_actions.append(action)


   def get_pending_actions(self):
      return self.pending_actions

   def clear_entity_pending_actions(self):
      self.pending_actions = []

   def clear_pending_actions(self, world):
      for action in self.get_pending_actions():
         world.unschedule_action(action)
      self.clear_entity_pending_actions()

   def entity_string(self):
      return ' '.join(['blacksmith', self.name, str(self.position.x),
         str(self.position.y), str(self.resource_limit),
         str(self.rate), str(self.resource_distance)])

class Obstacle:
   def __init__(self, name, position, imgs):
      self.name = name
      self.position = position
      self.imgs = imgs
      self.current_img = 0
      
   def get_name(self):
      return self.name
      
   def set_position(self, point):
      self.position = point

   def get_position(self):
      return self.position

   def get_images(self):
      return self.imgs

   def get_image(self):
      return self.imgs[self.current_img]
      
   def next_image(self):
      self.current_img = (self.current_img + 1) % len(self.imgs)

   def entity_string(self):
      return ' '.join(['obstacle', self.name, str(self.position.x),
         str(self.position.y)])

class OreBlob:
   def __init__(self, name, position, rate, imgs, animation_rate):
      self.name = name
      self.position = position
      self.rate = rate
      self.imgs = imgs
      self.current_img = 0
      self.animation_rate = animation_rate
      self.pending_actions = []
      
   def get_name(self):
      return self.name
      
   def set_position(self, point):
      self.position = point

   def get_position(self):
      return self.position

   def get_rate(self):
      return self.rate
      
   def get_images(self):
      return self.imgs

   def get_image(self):
      return self.imgs[self.current_img]
      
   def next_image(self):
      self.current_img = (self.current_img + 1) % len(self.imgs)

   def get_animation_rate(self):
      return self.animation_rate
      
   def remove_pending_action(self, action):
      self.pending_actions.remove(action)

   def add_pending_action(self, action):
      self.pending_actions.append(action)


   def get_pending_actions(self):
      return self.pending_actions

   def clear_entity_pending_actions(self):
      self.pending_actions = []

   def clear_pending_actions(self, world):
      for action in self.get_pending_actions():
         world.unschedule_action(action)
      self.clear_entity_pending_actions()

   def entity_string(self):
      return 'unknown'
      
   def blob_next_position(self, world, dest_pt):
      horiz = sign(dest_pt.x - self.position.x)
      new_pt = point.Point(self.position.x + horiz, self.position.y)

      if horiz == 0 or (world.is_occupied(new_pt) and
         not isinstance(world.get_tile_occupant(new_pt), Ore)):
         vert = sign(dest_pt.y - self.position.y)
         new_pt = point.Point(self.position.x, self.position.y + vert)

         if vert == 0 or (world.is_occupied(new_pt) and
            not isinstance(world.get_tile_occupant(new_pt), Ore)):
            new_pt = point.Point(self.position.x, self.position.y)

      return new_pt
      
   def blob_to_vein(self, world, vein):
      entity_pt = self.position
      if not vein:
         return ([entity_pt], False)
      vein_pt = vein.get_position()
      if adjacent(entity_pt, vein_pt):
         actions.remove_entity(world, vein)
         return ([vein_pt], True)
      else:
         new_pt = self.blob_next_position(world, vein_pt)
         old_entity = world.get_tile_occupant(new_pt)
         if isinstance(old_entity, Ore):
            actions.remove_entity(world, old_entity)
         return (world.move_entity(self, new_pt), False)
         
   def create_ore_blob_action(self, world, i_store):
      def action(current_ticks):
         self.remove_pending_action(action)

         entity_pt = self.position
         vein = world.find_nearest(entity_pt, Vein)
         (tiles, found) = self.blob_to_vein(world, vein)

         next_time = current_ticks + self.rate
         if found:
            quake = actions.create_quake(world, tiles[0], current_ticks, i_store)
            world.add_entity(quake)
            next_time = current_ticks + self.rate * 2

         actions.schedule_action(world, self,
            self.create_ore_blob_action(world, i_store),
            next_time)

         return tiles
      return action
      
class Quake:
   def __init__(self, name, position, imgs, animation_rate):
      self.name = name
      self.position = position
      self.imgs = imgs
      self.current_img = 0
      self.animation_rate = animation_rate
      self.pending_actions = []
      
   def get_name(self):
      return self.name
      
   def set_position(self, point):
      self.position = point

   def get_position(self):
      return self.position

   def get_images(self):
      return self.imgs

   def get_image(self):
      return self.imgs[self.current_img]
      
   def next_image(self):
      self.current_img = (self.current_img + 1) % len(self.imgs)

   def get_animation_rate(self):
      return self.animation_rate
      
   def remove_pending_action(self, action):
      self.pending_actions.remove(action)

   def add_pending_action(self, action):
      self.pending_actions.append(action)


   def get_pending_actions(self):
      return self.pending_actions

   def clear_entity_pending_actions(self):
      self.pending_actions = []

   def clear_pending_actions(self, world):
      for action in self.get_pending_actions():
         world.unschedule_action(action)
      self.clear_entity_pending_actions()

   def entity_string(self):
      return 'unknown'
      
      

      
      
def try_transform_miner_full(world, entity):
   new_entity = MinerNotFull(
      entity.get_name(), entity.get_resource_limit(),
      entity.get_position(), entity.get_rate(),
      entity.get_images(), entity.get_animation_rate())

   return new_entity
      
def try_transform_miner_not_full(world, entity):
   if entity.resource_count < entity.resource_limit:
      return entity
   else:
      new_entity = MinerFull(
         entity.get_name(), entity.get_resource_limit(), entity.get_position(),
         entity.get_rate(), entity.get_images(), entity.get_animation_rate())
      return new_entity
      
def try_transform_miner(world, entity, transform):
   new_entity = transform(world, entity)
   if entity != new_entity:
      entity.clear_pending_actions(world)
      world.remove_entity_at(entity.get_position())
      world.add_entity(new_entity)
      actions.schedule_animation(world, new_entity)

   return new_entity

def adjacent(pt1, pt2):
   return ((pt1.x == pt2.x and abs(pt1.y - pt2.y) == 1) or
      (pt1.y == pt2.y and abs(pt1.x - pt2.x) == 1))

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
