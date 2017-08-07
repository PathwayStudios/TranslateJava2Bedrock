# Prepare for MCPE 1+ - Pathway Studios (http://pathway.studio)
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


from pymclevel import TAG_List
from pymclevel import TAG_Byte
from pymclevel import TAG_Int
from pymclevel import TAG_Compound
from pymclevel import TAG_Short
from pymclevel import TAG_Double
from pymclevel import TAG_String
from pymclevel import TAG_Float
from pymclevel import TileEntity
from pymclevel import id_definitions
from pymclevel import leveldb
from pymclevel import leveldbpocket


displayName = "Prepare for MCPE 1+"
VERSION = "0.9.6"
#CHANGE LOG - 
# 0.9.0 - Big changes - refactored a ton of code. Closer to release.
# 0.9.1 - WHAT? Command block support? awwww yisssssss
# 0.9.2 - refactored Remove Flatlands and Fix Blocks to increase speed (huge selections still take a long time)
# 0.9.3 - fixed crash with click events on signs
# 0.9.4 - Added support for keeping some TE's inventories
# 0.9.5 - added ID associations (separate file)
# 0.9.6 - added remote support for associations and spawner support


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
		
inputs = ()				
if upgradeAssocations == 1:
	inputs =(("Associations File Upgraded to: "+idMappings["version"],"label"),
		("Prepare for MCPE 1+", "label"),
		("Export File Name:",("string","value=convter-to-pe-export.txt")),
		("Remove Flatlands:", False),
		("Fix Blocks:", False),
		("Caution: Fix Blocks and Remove Flatlands can take a *long* time if you have a lot if blocks selected. Try to keep your selection at a minimum", "label"),	
		("Prepare for MCPE 1+ :", False),
		("Dump TileEntity:", False),
		("Dump Entity:", False),
		("Testing:", False)
	)
elif associations == 0:
	inputs =(("**CAUTION ASSOCIATIONS FILE NOT FOUND**", "label"),
		("Prepare for MCPE 1+", "label"),
		("Export File Name:",("string","value=convter-to-pe-export.txt")),
		("Remove Flatlands:", False),
		("Fix Blocks:", False),
		("Caution: Fix Blocks and Remove Flatlands can take a *long* time if you have a lot if blocks selected. Try to keep your selection at a minimum", "label"),	
		("Prepare for MCPE 1+ :", False),
		("Dump TileEntity:", False),
		("Dump Entity:", False),
		("Testing:", False)
	)
else:
	inputs =(("Prepare for MCPE 1+", "label"),
		("Export File Name:",("string","value=convter-to-pe-export.txt")),
		("Remove Flatlands:", False),
		("Fix Blocks:", False),
		("Caution: Fix Blocks and Remove Flatlands can take a *long* time if you have a lot if blocks selected. Try to keep your selection at a minimum", "label"),	
		("Prepare for MCPE 1+ :", False),
		("Dump TileEntity:", False),
		("Dump Entity:", False),
		("Testing:", False)
	)


removeTileEntities = ['minecraft:structure_block']	
removeEntities = ['ArmorStand']
tileEntityNameReplacements = {'Control':'CommandBlock',
							  'Noteblock':'Music',
							  'EnchantingTable':'EnchantTable'}

flatlandsBlockIDs = ['2',
					 '3',
					 '7']	
					 
newTrapDoorDataValues = ['3',
						 '2',
						 '1',
						 '0',
						 '11',
						 '10',
						 '9',
						 '8',
						 '7',
						 '6',
						 '5',
						 '4',
						 '15',
						 '14',
						 '13',
						 '12']
						 
slabValuesMCPE = ['157',
				  '158',
				  '' ]

newSlabValuesMCPE = ['']

newSlabValueJava = ['']

flatlandsY = 4					   
							 

def fixID(id):
	id = id.replace("minecraft:","").capitalize()
	id = id.split("_")
	newid = ""
	for i in id:
		newid += i.capitalize()
	return newid

def stripID(id):
	return id.replace("minecraft:","")
	
def perform(level, box, options):
	start = time.time()
	print(start)
	file_name = options["Export File Name:"]

	if file_name == "":
		file_name = "convert-to-pe-export.txt"

	if file_name.find(".txt") < 0:
		file_name += ".txt"

	output_text = ''
	contents = ''
	
	if options["Testing:"]:
		notedChunks = [ ]
		count = 0
		for (chunk, slices, point) in level.getChunkSlices(box):
			for t in chunk.TileEntities:
				id = t["id"].value
				x = t["x"].value
				y = t["y"].value
				z = t["z"].value	
				if (x,y,z) in box and "StructureBlock" in id:
					blockid = level.blockAt(x,y,z)
					chunkX = t["x"].value / 16
					chunkZ = t["z"].value / 16	
					chunk.TileEntities.remove(t)
					#newte = TileEntity.Create(id)
					#newte = t
					#if not (chunkX,chunkZ) in notedChunks:
					#	if t["EntityId"].value == 32:
					#		print ("zombie spawner at: " + str(x)+" "+str(y)+" "+str(z))
					#		newte["EntityId"] = TAG_Int(47)
					#		notedChunks.append((chunkX,chunkZ))
					#		count += 1
					#newte["MaxNearbyEntities"] = TAG_Short(12)
					#newte["SpawnCount"] = TAG_Short(6)
					#newte["SpawnRange"] = TAG_Short(6)
					#newte["MaxSpawnDelay"] = TAG_Short(400)
					#newte["id"] = TAG_String(str(id))
					#chunk.TileEntities.append(newte)
					#level.setBlockAt(x, y, z, blockid)
					
					
		print(count)

	if options["Dump TileEntity:"]:
		checkedPositions = []
		evalue = []
		entitiess=""
		for (chunk, slices, point) in level.getChunkSlices(box):
			for t in chunk.TileEntities:				
				x = t["x"].value
				y = t["y"].value
				z = t["z"].value	
				id = t["id"].value	
				if (x,y,z) in box:
					block = level.blockAt(x,y,z)
					bdata = level.blockDataAt(x,y,z)
					print(block, bdata, x, y, z)
					print(str(t))
					contents += "----"+id+":"+str(bdata)+" "+str(x)+","+str(y)+","+str(z)+"\n"
					contents += str(chunk)+"\n"+ str(t) + "\n\n"
					output_text += contents
					
	if options["Dump Entity:"]:
		checkedPositions = []
		evalue = []
		entitiess=""
		for (chunk, slices, point) in level.getChunkSlices(box):
			for e in chunk.Entities:
				x = e["Pos"][0].value
				y = e["Pos"][1].value
				z = e["Pos"][2].value	
				id = e["id"].value	
				if (x,y,z) in box:
					print(str(e))
					contents += "----"+id+" "+str(x)+","+str(y)+","+str(z)+"\n"
					contents += str(chunk)+"\n"+ str(e) + "\n\n"
					output_text += contents

	if options["Remove Flatlands:"]:
		
		positions = itertools.product(
			xrange(box.minx, box.maxx),
			xrange(box.miny, min(box.maxy, flatlandsY)),
			xrange(box.minz, box.maxz))

		for x, y, z in positions:
			block = level.blockAt(x,y,z)
			if str(block) in flatlandsBlockIDs:
				level.setBlockAt(x, y, z, 0)

	if options["Fix Blocks:"]:

		positions = itertools.product(
			xrange(box.minx, box.maxx),
			xrange(box.miny, box.maxy),
			xrange(box.minz, box.maxz))

		for x, y, z in positions:
			block = level.blockAt(x,y,z)
			bdata = level.blockDataAt(x,y,z)
			if block == 96 or block == 167:
				level.setBlockDataAt(x, y, z, newTrapDoorDataValues[bdata])

					
	if options["Prepare for MCPE 1+ :"]:
		tileEntitiesToReplace = []
		tileEntitiesToRemove = []
		entitiesToRemove = []
		entitiesToUpdate = []
		tileEntityContainer = []
		entityContainer = []
		for (chunk, slices, point) in level.getChunkSlices(box):
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
							tileEntitiesToRemove.append((chunk, t))		
						else:
							tileEntitiesToReplace.append((chunk, t))
			for e in chunk.Entities:
				x = e["Pos"][0].value
				y = e["Pos"][1].value
				z = e["Pos"][2].value
				id = fixID(e["id"].value)
				coords = str(x) +","+ str(y) +","+str(z)	
				if (coords) not in entityContainer:	
					entityContainer.append(coords)					
					if (x,y,z) in box:
						entitiesToRemove.append((chunk, e))
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
				if id in tileEntityNameReplacements:
					id = tileEntityNameReplacements[id]
				blockid = level.blockAt(x,y,z)
				contents += "----"+id+" "+str(x)+","+str(y)+","+str(z)+"\n"
				contents += str(chunk)+"\n"+ str(t) + "\n\n"
				chunk.TileEntities.remove(t)
				newte = TileEntity.Create(id)
				TileEntity.setpos(newte, (x, y, z))
				if ("MobSpawner" in id):
					try:
						entityName = t["SpawnData"]["id"].value.replace("minecraft:","")
					except KeyError:
						entityName = t["EntityId"].value
					if (fixID(entityName) in idMappings["entities"]):
						newte = t
						del newte["SpawnData"]
						del newte["SpawnPotentials"]
						if entityName.isdigit():
							entityId = entityName
						else:
							entityId = idMappings["entities"][fixID(entityName)]
						newte["EntityId"] = TAG_Int(int(entityId))
					else:
						print("ENTITY NOT FOUND REPLACED WITH ZOMBIE: "+str(entityName).lower()+" "+str(x)+","+str(y)+","+str(z))
						contents += "ENTITY NOT FOUND REPLACED WITH ZOMBIE: "+str(entityName).lower()+" "+str(x)+","+str(y)+","+str(z)+"\n"
						newte = t
						del newte["SpawnData"]
						del newte["SpawnPotentials"]
						newte["EntityId"] = TAG_Int(32)
				if ("Items" in t) and (not "Items" in newte):
					newte["Items"]=TAG_List()
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
				if id == "CommandBlock":
					newte = t
					del newte["UpdateLastExecution"]
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
