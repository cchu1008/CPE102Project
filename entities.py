import point

class Background:
   def __init__(self, name, imgs):
      self.name = name
      self.imgs = imgs
      self.current_img = 0
      
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
      
   def entity_string(self):
      return ' '.join(['miner', self.name, str(self.position.x),
         str(self.position.y), str(self.resource_limit),
         str(self.rate), str(self.animation_rate)])
         
   def miner_to_ore(self, world, ore):
      entity_pt = self.position
      if not ore:
         return ([entity_pt], False)
      ore_pt = entities.get_position(ore)
      if adjacent(entity_pt, ore_pt):
         entities.set_resource_count(self, 
            1 + entities.get_resource_count(self))
         remove_entity(world, ore)
         return ([ore_pt], True)
      else:
         new_pt = next_position(world, entity_pt, ore_pt)
         return (world.move_entity(self, new_pt), False)
         
   def create_miner_not_full_action(self, world, i_store):
      def action(current_ticks):
         entities.remove_pending_action(self, action)

         entity_pt = self.position
         ore = world.find_nearest(entity_pt, entities.Ore)
         (tiles, found) = miner_to_ore(world, ore)

         new_entity = self
         if found:
            new_entity = try_transform_miner(world, self,
               try_transform_miner_not_full)

         schedule_action(world, new_entity,
            create_miner_action(world, new_entity, i_store),
            current_ticks + entities.get_rate(new_entity))
         return tiles
      return action

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
      
   def entity_string(self):
      return 'unknown'
      
   def miner_to_smith(self, world, smith):
      entity_pt = self.position
      if not smith:
         return ([entity_pt], False)
      smith_pt = entities.get_position(smith)
      if adjacent(entity_pt, smith_pt):
         entities.set_resource_count(smith, 
            entities.get_resource_count(smith) +
            self.resource_count)
         self.resource_count = 0
         return ([], True)
      else:
         new_pt = next_position(world, entity_pt, smith_pt)
         return (world.move_entity(self, new_pt), False)
         
   def create_miner_full_action(self, world, i_store):
      def action(current_ticks):
         entities.remove_pending_action(self, action)

         entity_pt = self.position
         smith = world.find_nearest(entity_pt, entities.Blacksmith)
         (tiles, found) = miner_to_smith(world, smith)

         new_entity = self
         if found:
            new_entity = try_transform_miner(world, self,
               try_transform_miner_full)

         schedule_action(world, new_entity,
            create_miner_action(world, new_entity, i_store),
            current_ticks + entities.get_rate(new_entity))
         return tiles
      return action

class Vein:
   def __init__(self, name, rate, position, imgs, resource_distance=1):
      self.name = name
      self.position = position
      self.rate = rate
      self.imgs = imgs
      self.current_img = 0
      self.resource_distance = resource_distance
      self.pending_actions = []

   def entity_string(self):
      return ' '.join(['vein', self.name, str(self.position.x),
         str(self.position.y), str(self.rate),
         str(self.resource_distance)])
         
         
   def create_vein_action(self, world, i_store):
      def action(current_ticks):
         entities.remove_pending_action(self, action)

         open_pt = find_open_around(world, self.position,
            self.resource_distance)
         if open_pt:
            ore = create_ore(world,
               "ore - " + self.name + " - " + str(current_ticks),
               open_pt, current_ticks, i_store)
            world.add_entity(ore)
            tiles = [open_pt]
         else:
            tiles = []

         schedule_action(world, self,
            create_vein_action(world, i_store),
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

   def entity_string(self):
      return 'unknown'
      
   def blob_next_position(self, world, dest_pt):
      horiz = sign(dest_pt.x - self.position.x)
      new_pt = point.Point(self.position.x + horiz, self.position.y)

      if horiz == 0 or (world.is_occupied(new_pt) and
         not isinstance(world.get_tile_occupant(new_pt),
         entities.Ore)):
         vert = sign(dest_pt.y - self.position.y)
         new_pt = point.Point(self.position.x, self.position.y + vert)

         if vert == 0 or (world.is_occupied(new_pt) and
            not isinstance(world.get_tile_occupant(new_pt),
            entities.Ore)):
            new_pt = point.Point(self.position.x, self.position.y)

      return new_pt
      
   def blob_to_vein(self, world, vein):
      entity_pt = self.position
      if not vein:
         return ([entity_pt], False)
      vein_pt = entities.get_position(vein)
      if adjacent(entity_pt, vein_pt):
         remove_entity(world, vein)
         return ([vein_pt], True)
      else:
         new_pt = blob_next_position(world, entity_pt, vein_pt)
         old_entity = world.get_tile_occupant(new_pt)
         if isinstance(old_entity, entities.Ore):
            remove_entity(world, old_entity)
         return (world.move_entity(self, new_pt), False)
         
   def create_ore_blob_action(self, world, i_store):
      def action(current_ticks):
         entities.remove_pending_action(self, action)

         entity_pt = self.position
         vein = world.find_nearest(entity_pt, entities.Vein)
         (tiles, found) = blob_to_vein(world, vein)

         next_time = current_ticks + entities.get_rate(self)
         if found:
            quake = create_quake(world, tiles[0], current_ticks, i_store)
            world.add_entity(quake)
            next_time = current_ticks + self.rate * 2

         schedule_action(world, self,
            create_ore_blob_action(world, i_store),
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
      
   def entity_string(self):
      return 'unknown'

def get_resource_distance(entity):
   return entity.resource_distance

def get_animation_rate(entity):
   return entity.animation_rate
      
def get_resource_count(entity):
   return entity.resource_count
   
def get_resource_limit(entity):
   return entity.resource_limit
      
def set_resource_count(entity, n):
   entity.resource_count = n

def get_rate(entity):
   return entity.rate
   
def get_name(entity):
   return entity.name

def get_images(entity):
   return entity.imgs

def get_image(entity):
   return entity.imgs[entity.current_img]
   
def set_position(entity, point):
   entity.position = point

def get_position(entity):
   return entity.position

def remove_pending_action(entity, action):
   if hasattr(entity, "pending_actions"):
      entity.pending_actions.remove(action)

def add_pending_action(entity, action):
   if hasattr(entity, "pending_actions"):
      entity.pending_actions.append(action)


def get_pending_actions(entity):
   if hasattr(entity, "pending_actions"):
      return entity.pending_actions
   else:
      return []

def clear_pending_actions(entity):
   if hasattr(entity, "pending_actions"):
      entity.pending_actions = []


def next_image(entity):
   entity.current_img = (entity.current_img + 1) % len(entity.imgs)
