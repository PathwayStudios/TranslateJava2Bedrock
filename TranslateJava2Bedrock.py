# Translate Java 2 Bedrock - Pathway Studios (http://pathway.studio)
# Copyright (C) 2017  Pathway Studios

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os.path
import warnings
import time
import itertools
import unicodedata
import pprint
import json
import urllib2


from pymclevel import TAG_List, TAG_Byte, TAG_Int, TAG_Compound, TAG_Short, TAG_Double, TAG_String, TAG_Float, TileEntity, id_definitions, leveldb, leveldbpocket


displayName = "Translate Java 2 Bedrock"
VERSION = "0.9.7"
#CHANGE LOG - 
# 0.9.0 - Big changes - refactored a ton of code. Closer to release.
# 0.9.1 - WHAT? Command block support? awwww yisssssss
# 0.9.2 - refactored Remove Flatlands and Fix Blocks to increase speed (huge selections still take a long time)
# 0.9.3 - fixed crash with click events on signs
# 0.9.4 - Added support for keeping some TE's inventories
# 0.9.5 - added ID associations (separate file)
# 0.9.6 - added remote support for associations and spawner support


# get pe-item-associations file, and check if user has latest copy
associations = 0
upgradeAssocations = 9
idMappings = []
idMappingsRemote = []

if os.path.isfile('pe-item-associations.json'): 
	idMappings = json.load(open('pe-item-associations.json'))
	associations = 1

req = urllib2.Request('http://pathway.studio/resources/pe-item-associations.json')
url=urllib2		

try:
	response = urllib2.urlopen(req)
	idMappingsRemote = json.loads(response.read())

except url.URLError as e:
	print "Error getting associations file: " +str(e.reason)
	
if ("version" in idMappingsRemote): 
	if ("version" in idMappings):
		if idMappingsRemote["version"] > idMappings["version"]:
			with open("pe-item-associations.json", "w") as text_file:
				json.dump(idMappingsRemote, text_file, ensure_ascii=False)
			idMappings = idMappingsRemote
			associations = 1
			upgradeAssocations = 1
			print("Updated associations file to version "+idMappings["version"])
	else:
		with open("pe-item-associations.json", "w") as text_file:
			json.dump(idMappingsRemote, text_file)	
		idMappings = idMappingsRemote
		associations = 1
		upgradeAssocations = 1
		print("Updated associations file to version "+idMappings["version"])
		
# build interface informing user of pe-associates was upgraded was upgraded		
inputs = ()				
if upgradeAssocations == 1:
	inputs =(("Associations File Upgraded to: "+idMappings["version"],"label"),
		("Translate Java 2 Bedrock", "label"),
		("Export File Name:",("string","value=translate-java-2-bedrock.txt")),
		("Java Mode:", False),
		("Prepare for Bedrock:", False)
	)
elif associations == 0:
	inputs =(("**CAUTION ASSOCIATIONS FILE NOT FOUND**", "label"),
		("Translate Java 2 Bedrock", "label"),
		("Export File Name:",("string","value=translate-java-2-bedrock.txt")),
		("Java Mode:", False),
		("Prepare for Bedrock:", False)
	)
else:
	inputs =(("Translate Java 2 Bedrock", "label"),
		("Export File Name:",("string","value=translate-java-2-bedrock.txt")),
		("Java Mode:", False),
		("Prepare for Bedrock:", False)
	)

# list of tile entities to remove instead of trying to translate
removeTileEntities = ['minecraft:structure_block']	
# removeEntities is currently unused until entity support is added
# currently ALL entities are removed
removeEntities = ['ArmorStand']

# some tile entity IDs have changed (support for pre-item name IDs)
tileEntityNameReplacements = {'Control':'CommandBlock',
							  'Noteblock':'Music',
							  'EnchantingTable':'EnchantTable'}
				   
							 
# convert ID name to bedrock version (e.g. minecraft:command_block to CommandBlock)
def fixID(id):
	if id.find("_") > 0:
		id = id.split("_")
		newid = ""
		for i in id:
			newid += i.capitalize()
		return newid
	else:
		return id
# remove minecraft namespace
def stripID(id):
	id = str(id)
	if id.find("minecraft:") > 0:
		return id.replace("minecraft:","")
	else:
		return
	
def perform(level, box, options):
	start = time.time()
	print(start)
	file_name = options["Export File Name:"]

	if file_name == "":
		file_name = "translate-java-2-bedrock.txt"

	if file_name.find(".txt") < 0:
		file_name += ".txt"

	output_text = ''
	contents = ''
	
					
	if options["Prepare for Bedrock:"]:
		tileEntitiesToReplace = []
		tileEntitiesToRemove = []
		entitiesToRemove = []
		entitiesToUpdate = []
		tileEntityContainer = []
		entityContainer = []
		for (chunk, slices, point) in level.getChunkSlices(box):
			# get list of all entities in selection
			for t in chunk.TileEntities:				
				x = t["x"].value
				y = t["y"].value
				z = t["z"].value
				coords = str(x) +","+ str(y) +","+str(z)
				id = fixID(t["id"].value)
				if (coords) not in tileEntityContainer:
					tileEntityContainer.append(coords)
					if (x,y,z) in box:
						if id in removeTileEntities:
							# tile entities that need to be removed
							tileEntitiesToRemove.append((chunk, t))		
						else:
							# tile entities that need to be translated
							tileEntitiesToReplace.append((chunk, t))
			# get all entities in selection
			for e in chunk.Entities:
				x = e["Pos"][0].value
				y = e["Pos"][1].value
				z = e["Pos"][2].value
				id = fixID(e["id"].value)
				coords = str(x) +","+ str(y) +","+str(z)	
				if (coords) not in entityContainer:	
					entityContainer.append(coords)					
					if (x,y,z) in box:
						# delete tile entity
						entitiesToRemove.append((chunk, e))
						# removed replacement code until entities can be translated
						#if (id in removeEntities):
							#entitiesToRemove.append((chunk, e))	
						#else:
							#entitiesToUpdate.append((chunk, e))
		
		if tileEntitiesToReplace:
			for (chunk, t) in tileEntitiesToReplace:
				iIgnore = 0
				x = t["x"].value
				y = t["y"].value
				z = t["z"].value
				id = fixID(t["id"].value)	
				# check to see if the ID needs to be translated
				if id in tileEntityNameReplacements:
					id = tileEntityNameReplacements[id]
				blockid = level.blockAt(x,y,z)
				contents += "----"+id+" "+str(x)+","+str(y)+","+str(z)+"\n"
				contents += str(chunk)+"\n"+ str(t) + "\n\n"
				chunk.TileEntities.remove(t)
				newte = TileEntity.Create(id)
				TileEntity.setpos(newte, (x, y, z))
				# rewrite spawner data - no features carried over as bedrock doesn't support
				# SpawnData or SpawnPotentials
				# adding MinSpawnDelay, MaxSpawnDelay, MaxNearbyEntities, etc is a good idea
				if ("MobSpawner" in id):
					try:
						entityName = t["SpawnData"]["id"].value.replace("minecraft:","")
					except KeyError:
						entityName = t["EntityId"].value
					if not str(entityName).isdigit():
						entityName = fixID(entityName)
					if (entityName in idMappings["entities"]):
						newte = t
						if "SpawnData" in newte:
							del newte["SpawnData"]
						if "SpawnPotentials" in newte:
							del newte["SpawnPotentials"]
						if entityName.isdigit():
							entityId = entityName
						else:
							entityId = idMappings["entities"][fixID(entityName)]
						newte["EntityId"] = TAG_Int(int(entityId))
					else:
						print("ENTITY NOT FOUND REPLACED WITH ZOMBIE: "+str(entityName)+" "+str(x)+","+str(y)+","+str(z))
						contents += "ENTITY NOT FOUND REPLACED WITH ZOMBIE: "+str(entityName)+" "+str(x)+","+str(y)+","+str(z)+"\n"
						newte = t
						if "SpawnData" in newte:						
							del newte["SpawnData"]
						if "SpawnPotentials" in newte:							
							del newte["SpawnPotentials"]
						newte["EntityId"] = TAG_Int(32)
				# MCEdit doesn't add all the needed tags when creating a new tile entity
				if ("Items" in t) and (not "Items" in newte):
					newte["Items"]=TAG_List()
				# if the tile entity has an inventory, convert the inventory
				if ("Items" in t) and ("Items" in newte):
					for i in t["Items"]:
						if not str(i["id"].value).isdigit():
							itemNew = stripID(i["id"].value)
							if itemNew in idMappings["items"]:
								idItems = idMappings["items"][itemNew]	
							elif itemNew in idMappings:
								idItems = idMappings[itemNew]["id"]
							else:
								idItems = 248
								print("ITEM NOT FOUND: "+str(i["id"].value)+" "+str(x)+","+str(y)+","+str(z))
								contents += "ITEM NOT FOUND: "+str(i["id"].value)+" "+str(x)+","+str(y)+","+str(z)+"\n"
						else:
							idItems = i["id"].value
						idItems = int(idItems)					
						item = TAG_Compound()
						item["id"] = TAG_Short(idItems)
						if stripID(i["id"].value) == "lava_bucket":
							item["Damage"] = TAG_Short(10)
						elif stripID(i["id"].value) == "water_bucket":
							item["Damage"] = TAG_Short(8)
						elif stripID(i["id"].value) == "milk_bucket":	
							item["Damage"] = TAG_Short(1)
						else:
							item["Damage"] = TAG_Short(i["Damage"].value)
						item["Count"] = TAG_Byte(i["Count"].value)
						item["Slot"] = TAG_Byte(i["Slot"].value)
						if "tag" in i:
							pset=0
							item["tag"] = TAG_Compound(i["tag"].value)
							if ("Potion" in item["tag"]) and (not itemNew in idMappings):
								potion = stripID(item["tag"]["Potion"].value)
								if potion in idMappings["potions"]:
									item["Damage"] = TAG_Short(int(idMappings["potions"][potion]))
							elif ("Potion" in item["tag"]) and (itemNew in idMappings):
								potion = stripID(item["tag"]["Potion"].value)
								item["Damage"] = TAG_Short(int(idMappings[itemNew][potion]))
								del item["tag"]["Potion"]
							if ("ench" in i["tag"]):
								enchHolder = TAG_List()
								for e in i["tag"]["ench"]:
									ench = TAG_Compound()
									enchId = e["id"].value
									enchLvl = e["lvl"].value
									if str(enchId) in idMappings["enchantments"]:
										enchId = int(idMappings["enchantments"][str(enchId)])
										ench["lvl"] = TAG_Short(enchLvl)
										ench["id"] = TAG_Short(enchId)	
										enchHolder.append(ench)
								item["tag"]["ench"] = enchHolder
							if "StoredEnchantments" in i["tag"]:
								enchHolder = TAG_List()
								for e in i["tag"]["StoredEnchantments"]:
									ench = TAG_Compound()
									enchId = e["id"].value
									enchLvl = e["lvl"].value
									if str(enchId) in idMappings["enchantments"]:
										enchId = int(idMappings["enchantments"][str(enchId)])
										ench["lvl"] = TAG_Short(enchLvl)
										ench["id"] = TAG_Short(enchId)	
										enchHolder.append(ench)
								item["tag"]["ench"] = enchHolder
								del item["tag"]["StoredEnchantments"]
							if "CanPlaceOn" in i["tag"]:
								canPlaceOn = TAG_List()
								for p in i["tag"]["CanPlaceOn"]:
									canPlaceOn.append(TAG_String(p.value.replace("minecraft:","")))
								del item["tag"]["CanPlaceOn"]
								item["CanPlaceOn"] = canPlaceOn
							if "CanDestroy" in i["tag"]:
								canDestroy = TAG_List()
								for p in i["tag"]["CanDestroy"]:
									canDestroy.append(TAG_String(p.value.replace("minecraft:","")))
								del item["tag"]["CanDestroy"]
								item["CanDestroy"] = canDestroy
						newte["Items"].append(item)
				# convert command block data after fixing the ID earlier
				if id == "CommandBlock":
					newte = t
					if "UpdateLastExecution" in newte:
						del newte["UpdateLastExecution"]
					if "auto" not in newte:
						newte["auto"] = TAG_Byte(0)
					if "powered" not in newte:
						newte["powered"] = TAG_Byte(0)				
					if "SuccessCount" not in newte:
						newte["SuccessCount"] = TAG_Int(0)
					if "conditionMet" not in newte:
						newte["conditionMet"] = TAG_Byte(0)		
					if "TrackOutput" not in newte:
						newte["TrackOutput"] = TAG_Byte(0)		
					if ("CustomName" not in newte) or newte["CustomName"] == TAG_String(u'@'):
						newte["CustomName"] = TAG_String('')
				# my attempt at converting signs with or without json data
				# still probably breaks some (most?) signs that are json formatted
				if id == "Sign":
					if "Text1" in t:
						if t["Text1"].value.find('"text":') > 0:
							text1 = t["Text1"].value
							text1 = json.loads(text1)
							text1 = text1["text"]
							newte["Text1"] = TAG_String(text1)
						else:
							text1 = t["Text1"].value
							if not text1 == "":
								if (text1[0] == '"' and text1[:1] == '"'):
									text1 = text1[:-1]
									text1 = text1[1:]
							newte["Text1"] = TAG_String(text1)
					if "Text2" in t:
						if t["Text2"].value.find('"text":') > 0:
							text2 = t["Text2"].value
							text2 = json.loads(text2)
							text2 = text2["text"]
							newte["Text2"] = TAG_String(text2)
						else:
							text2 = t["Text2"].value
							if not text2 == "":
								if (text2[0] == '"' and text2[:1] == '"'):
									text2 = text2[:-1]
									text2 = text2[1:]
							newte["Text2"] = TAG_String(text2)
					if "Text3" in t:
						if t["Text3"].value.find('"text":') > 0:
							text3 = t["Text3"].value
							text3 = json.loads(text3)
							text3 = text3["text"]
							newte["Text3"] = TAG_String(text3)
						else:
							text3 = t["Text3"].value
							if not text3 == "":
								if (text3[0] == '"' and text3[:1] == '"'):
									text3 = text3[:-1]
									text3 = text3[1:]
							newte["Text3"] = TAG_String(text3)
					if "Text4" in t:
						if t["Text4"].value.find('"text":') > 0:
							text4 = t["Text4"].value
							text4 = json.loads(text4)
							text4 = text4["text"]
							newte["Text4"] = TAG_String(text4)
						else:
							text4 = t["Text4"].value
							if not text4 == "":
								if (text4[0] == '"' and text4[:1] == '"'):
									text4 = text4[:-1]
									text4 = text4[1:]
							newte["Text4"] = TAG_String(text4)
				# convert new style brewing stands (with blaze powder) to old style
				# will need to be reverted for 1.2 (which uses blaze powder)
				# also translates some tags
				if id == "BrewingStand":
					itemHolder = TAG_List()
					if "BrewTime" in t:
						newte["CookTime"] = t["BrewTime"]
					else:
						newte["CookTime"] = t["CookTime"]
					for i in t["Items"]:
						item = TAG_Compound()
						if i["Slot"].value == 3:
							slotID = stripID(i["id"].value)
							slotID = idMappings['items'][slotID]
							item["Slot"] = TAG_Byte(0)
							item["id"] = TAG_Short(int(slotID))
							item["Damage"] = i["Damage"]
							item["Count"] = i["Count"]
						elif i["Slot"].value == 0:
							slotID = stripID(i["id"].value)
							slotID = idMappings['items'][slotID]
							item["Slot"] = TAG_Byte(1)
							item["Count"] = i["Count"]
							item["id"] = TAG_Short(int(slotID))
							if "tag" in i:
								potionType = stripID(i["tag"]["Potion"].value)
								item["Damage"] = TAG_Short(int(idMappings['potions'][potionType]))
							else:
								potionType = i["Damage"].value
								item["Damage"] = TAG_Short(int(idMappings['potions'][potionType]))
						elif i["Slot"].value == 1:
							slotID = stripID(i["id"].value)
							slotID = idMappings['items'][slotID]
							item["Slot"] = TAG_Byte(2)	
							item["Count"] = i["Count"]
							item["id"] = TAG_Short(int(slotID))
							if "tag" in i:
								potionType = stripID(i["tag"]["Potion"].value)
								item["Damage"] = TAG_Short(int(idMappings['potions'][potionType]))
							else:
								potionType = i["Damage"].value
								item["Damage"] = TAG_Short(int(idMappings['potions'][potionType]))
						elif i["Slot"].value == 2:
							slotID = stripID(i["id"].value)
							slotID = idMappings['items'][slotID]
							item["Slot"] = TAG_Byte(3)
							item["Count"] = i["Count"]
							item["id"] = TAG_Short(int(slotID))
							if "tag" in i:
								potionType = stripID(i["tag"]["Potion"].value)
								item["Damage"] = TAG_Short(int(idMappings['potions'][potionType]))
							else:
								potionType = i["Damage"].value
								item["Damage"] = TAG_Short(int(idMappings['potions'][potionType]))
						itemHolder.append(item)
					newte["Items"] = itemHolder
				newte["id"] = TAG_String(str(id))
				chunk.TileEntities.append(newte)
				# playing around with java mode. If enabled it removes the block be keeps
				# the tile entity data. usecase would be to copy the tile entity data over
				# a world converted with a different tool
				if options["Java Mode:"]:
					level.setBlockAt(x, y, z, 0)
				else: 
					level.setBlockAt(x, y, z, blockid)
								
		if tileEntitiesToRemove:
			for (chunk, t) in tileEntitiesToRemove:
				x = t["x"].value
				y = t["y"].value
				z = t["z"].value
				id = fixID(t["id"].value)	
				contents += "----"+id+" "+str(x)+","+str(y)+","+str(z)+"\n"
				contents += str(chunk)+"\n"+ str(t) + "\n\n"
				chunk.TileEntities.remove(t)
				level.setBlockAt(x, y, z, 0)
		
		if 	entitiesToRemove:
			for (chunk, e) in entitiesToRemove:
				x = e["Pos"][0].value
				y = e["Pos"][1].value
				z = e["Pos"][2].value
				id = fixID(e["id"].value)
				contents += "----"+id+" "+str(x)+","+str(y)+","+str(z)+"\n"
				contents += str(chunk)+"\n"+ str(e) + "\n\n"
				chunk.Entities.remove(e)

		# beginning of translate entity data
		# not currently used
		if 	entitiesToUpdate:
			for (chunk, e) in entitiesToUpdate:
				x = e["Pos"][0].value
				y = e["Pos"][1].value
				z = e["Pos"][2].value
				id = fixID(e["id"].value)
				newEntity = e
				newEntity["id"] = TAG_String(id)
				contents += "----"+id+" "+str(x)+","+str(y)+","+str(z)+"\n"
				contents += str(chunk)+"\n"+ str(e) + "\n\n"
				chunk.Entities.remove(e)
				chunk.Entities.append(newEntity)
		
		output_text += contents
		chunk.dirty = True
	output_text = output_text.encode('utf-8')
	with open(file_name, "w") as text_file:
		text_file.write(output_text)	
	end = time.time()
	finalTime = end - start
	print(end)
	print("It took " + str(finalTime) + " seconds to complete the requested operation")	
