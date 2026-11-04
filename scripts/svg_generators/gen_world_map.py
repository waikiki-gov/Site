#!/usr/bin/env python3
"""Generator for World Islands infrastructure SVG map."""

import math
import sys
from pathlib import Path

try:
    from map_common import n, pt, poly_path, smooth_island, hotspot, map_header, update_island_map
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from map_common import n, pt, poly_path, smooth_island, hotspot, map_header, update_island_map


# ==========================================================================
# WORLD ISLANDS (RECOGNIZABLE CONTINENTS: MAJOR CORES + SATELLITE ISLES)
# ==========================================================================
WORLD_ISLES = [
    # === NORTH AMERICA (27 Islands: Arctic, Canada, US, Florida, Baja, Mexico, Central America, Caribbean) ===
    {'name': 'Alaska North Slope', 'cx': 238, 'cy': 161, 'rx': 17, 'ry': 12, 'rot': -10, 'green': True},
    {'name': 'Alaska Peninsula and Aleutians', 'cx': 210, 'cy': 181, 'rx': 14, 'ry': 8, 'rot': -25},
    {'name': 'Yukon and Northwest Territories', 'cx': 274, 'cy': 148, 'rx': 17, 'ry': 13, 'rot': 10, 'green': True},
    {'name': 'Canadian Arctic Islands', 'cx': 312, 'cy': 126, 'rx': 21, 'ry': 12, 'rot': 5, 'sand_light': True},
    {'name': 'Baffin Island', 'cx': 359, 'cy': 123, 'rx': 17, 'ry': 13, 'rot': 25, 'sand_light': True},
    {'name': 'Greenland Isle', 'cx': 424, 'cy': 112, 'rx': 25, 'ry': 26, 'rot': 20, 'sand_light': True},
    {'name': 'Western Canada Alberta', 'cx': 266, 'cy': 186, 'rx': 15, 'ry': 14, 'rot': -15, 'green': True},
    {'name': 'Canadian Rockies and British Columbia', 'cx': 236, 'cy': 197, 'rx': 12, 'ry': 15, 'rot': 15, 'shape': 'arc', 'green': True},
    {'name': 'Canadian Shield Ontario', 'cx': 308, 'cy': 174, 'rx': 20, 'ry': 15, 'rot': 10, 'green': True},
    {'name': 'Quebec and Labrador', 'cx': 361, 'cy': 164, 'rx': 21, 'ry': 17, 'rot': 15, 'green': True},
    {'name': 'Newfoundland and Maritimes', 'cx': 404, 'cy': 178, 'rx': 14, 'ry': 12, 'rot': 25, 'green': True},
    {'name': 'US Pacific Northwest', 'cx': 244, 'cy': 230, 'rx': 13, 'ry': 15, 'rot': 15, 'shape': 'arc'},
    {'name': 'California Coast', 'cx': 248, 'cy': 266, 'rx': 11, 'ry': 16, 'rot': 20, 'shape': 'arc'},
    {'name': 'US Rocky Mountains and Plains', 'cx': 286, 'cy': 224, 'rx': 19, 'ry': 15, 'rot': 0},
    {'name': 'US Midwest and Great Lakes', 'cx': 331, 'cy': 214, 'rx': 19, 'ry': 15, 'rot': 5, 'green': True, 'hub': 'na'},
    {'name': 'US East Coast and New England', 'cx': 374, 'cy': 212, 'rx': 17, 'ry': 16, 'rot': -25, 'green': True},
    {'name': 'US South and Gulf Coast', 'cx': 342, 'cy': 256, 'rx': 21, 'ry': 14, 'rot': -5},
    {'name': 'Texas and Southern Great Plains', 'cx': 298, 'cy': 260, 'rx': 16, 'ry': 14, 'rot': 0, 'shape': 'taper'},
    {'name': 'Florida Peninsula', 'cx': 382, 'cy': 268, 'rx': 10, 'ry': 16, 'rot': -30},
    {'name': 'Baja California', 'cx': 246, 'cy': 304, 'rx': 6, 'ry': 16, 'rot': 25, 'shape': 'arc'},
    {'name': 'Northern Mexico', 'cx': 278, 'cy': 296, 'rx': 16, 'ry': 14, 'rot': 15},
    {'name': 'Southern Mexico', 'cx': 298, 'cy': 328, 'rx': 14, 'ry': 13, 'rot': 25, 'shape': 'taper'},
    {'name': 'Yucatan Peninsula', 'cx': 338, 'cy': 318, 'rx': 13, 'ry': 11, 'rot': 20, 'shape': 'taper', 'green': True},
    {'name': 'Central America Isthmus', 'cx': 328, 'cy': 352, 'rx': 11, 'ry': 8, 'rot': 35, 'shape': 'arc'},
    {'name': 'Cuba and Greater Antilles', 'cx': 398, 'cy': 304, 'rx': 17, 'ry': 7, 'rot': -15},
    {'name': 'Bahamas and Caribbean Chain', 'cx': 424, 'cy': 322, 'rx': 9, 'ry': 6, 'rot': 25},
    {'name': 'Hawaii Pacific Outpost', 'cx': 155, 'cy': 255, 'rx': 10, 'ry': 7, 'rot': 20},

    # === SOUTH AMERICA (16 Islands: Colombia, Venezuela, Guyana, Amazon, Brazil, Andes, Argentina, Patagonia) ===
    {'name': 'Colombia and Northern Andes', 'cx': 354, 'cy': 382, 'rx': 15, 'ry': 13, 'rot': -20},
    {'name': 'Venezuela and Orinoco', 'cx': 390, 'cy': 370, 'rx': 17, 'ry': 11, 'rot': 10, 'green': True},
    {'name': 'Guyana Coast', 'cx': 424, 'cy': 378, 'rx': 13, 'ry': 9, 'rot': 20, 'green': True},
    {'name': 'Peru and Central Andes', 'cx': 342, 'cy': 420, 'rx': 13, 'ry': 19, 'rot': -15},
    {'name': 'Amazon Basin Heart', 'cx': 386, 'cy': 409, 'rx': 22, 'ry': 20, 'rot': 0, 'green': True},
    {'name': 'Brazil Northeast Bulge', 'cx': 447, 'cy': 415, 'rx': 20, 'ry': 16, 'rot': 20, 'green': True},
    {'name': 'Central Brazil and Cerrado Plateau', 'cx': 415, 'cy': 438, 'rx': 16, 'ry': 15, 'rot': 10, 'green': True},
    {'name': 'Bolivia and Pantanal', 'cx': 380, 'cy': 448, 'rx': 16, 'ry': 15, 'rot': 5},
    {'name': 'Paraguay and Gran Chaco Basin', 'cx': 366, 'cy': 479, 'rx': 13, 'ry': 14, 'rot': 5},
    {'name': 'Brazil Southeast Coast', 'cx': 436, 'cy': 469, 'rx': 18, 'ry': 17, 'rot': 25, 'green': True},
    {'name': 'Chile Andes Strip', 'cx': 338, 'cy': 489, 'rx': 9, 'ry': 25, 'rot': 8, 'shape': 'arc'},
    {'name': 'Argentina Pampas Core', 'cx': 385, 'cy': 512, 'rx': 17, 'ry': 19, 'rot': 5, 'shape': 'taper'},
    {'name': 'Uruguay and Rio de la Plata', 'cx': 418, 'cy': 505, 'rx': 12, 'ry': 12, 'rot': 15, 'green': True},
    {'name': 'Patagonia Southern Wedge', 'cx': 369, 'cy': 547, 'rx': 13, 'ry': 15, 'rot': 8, 'shape': 'taper'},
    {'name': 'Tierra del Fuego', 'cx': 379, 'cy': 572, 'rx': 11, 'ry': 7, 'rot': 10},
    {'name': 'Falkland Islands', 'cx': 402, 'cy': 565, 'rx': 7, 'ry': 5, 'rot': 0},

    # === ATLANTIC AND EUROPE (16 Islands: Iceland, Ireland, Great Britain, Scandinavia, Western Europe, Central Europe, Iberia, Italy, Greece, East Europe) ===
    {'name': 'Iceland', 'cx': 494, 'cy': 128, 'rx': 13, 'ry': 9, 'rot': -10, 'sand_light': True},
    {'name': 'Ireland', 'cx': 498, 'cy': 176, 'rx': 9, 'ry': 12, 'rot': 15},
    {'name': 'Great Britain', 'cx': 524, 'cy': 166, 'rx': 12, 'ry': 20, 'rot': -20, 'shape': 'arc'},
    {'name': 'Norway Fjord Coast', 'cx': 558, 'cy': 130, 'rx': 11, 'ry': 20, 'rot': 20, 'shape': 'arc', 'green': True},
    {'name': 'Denmark and Jutland Peninsula', 'cx': 564, 'cy': 168, 'rx': 9, 'ry': 13, 'rot': 10, 'shape': 'arc', 'green': True},
    {'name': 'Sweden and Finland', 'cx': 592, 'cy': 134, 'rx': 15, 'ry': 20, 'rot': 15, 'green': True},
    {'name': 'Western Europe Mainland Core', 'cx': 544, 'cy': 214, 'rx': 18, 'ry': 14, 'rot': 5, 'green': True, 'hub': 'eu'},
    {'name': 'France and Biscay Bay', 'cx': 513, 'cy': 230, 'rx': 13, 'ry': 13, 'rot': -10, 'green': True},
    {'name': 'Central Europe Germany and Alps', 'cx': 582, 'cy': 204, 'rx': 15, 'ry': 13, 'rot': 0, 'green': True},
    {'name': 'Iberian Peninsula', 'cx': 500, 'cy': 260, 'rx': 16, 'ry': 15, 'rot': -10},
    {'name': 'Italy Boot Peninsula', 'cx': 564, 'cy': 260, 'rx': 8, 'ry': 15, 'rot': 35},
    {'name': 'Sicily and Malta', 'cx': 562, 'cy': 288, 'rx': 6, 'ry': 4, 'rot': -15},
    {'name': 'Balkans and Greece', 'cx': 602, 'cy': 256, 'rx': 14, 'ry': 13, 'rot': 15},
    {'name': 'Danube Basin and Romania', 'cx': 615, 'cy': 225, 'rx': 14, 'ry': 12, 'rot': 15, 'green': True},
    {'name': 'Poland and Baltic States', 'cx': 618, 'cy': 178, 'rx': 16, 'ry': 13, 'rot': 10, 'green': True},
    {'name': 'Eastern Europe Ukraine Plains', 'cx': 647, 'cy': 210, 'rx': 17, 'ry': 15, 'rot': 5},

    # === AFRICA (18 Islands: Morocco, Sahara, Libya, Egypt, Senegal, Guinea Coast, Nigeria, Sudan, Horn, Congo, Rift, Angola, Cape, Madagascar) ===
    {'name': 'Morocco and Atlas', 'cx': 503, 'cy': 320, 'rx': 14, 'ry': 10, 'rot': -15},
    {'name': 'Sahara Core Northwest', 'cx': 540, 'cy': 326, 'rx': 19, 'ry': 14, 'rot': 0},
    {'name': 'Libya and Central Sahara', 'cx': 581, 'cy': 326, 'rx': 17, 'ry': 13, 'rot': 0},
    {'name': 'Egypt and Nile Delta', 'cx': 622, 'cy': 318, 'rx': 17, 'ry': 13, 'rot': 15},
    {'name': 'West Africa Senegal Bulge', 'cx': 476, 'cy': 362, 'rx': 15, 'ry': 13, 'rot': -25},
    {'name': 'Gulf of Guinea Ivory Coast', 'cx': 514, 'cy': 368, 'rx': 17, 'ry': 11, 'rot': -5, 'green': True},
    {'name': 'Nigeria and Sahel', 'cx': 558, 'cy': 364, 'rx': 18, 'ry': 13, 'rot': 0},
    {'name': 'Sudan and Nubia Basin', 'cx': 616, 'cy': 362, 'rx': 16, 'ry': 13, 'rot': 15},
    {'name': 'Horn of Africa Somalia', 'cx': 658, 'cy': 366, 'rx': 17, 'ry': 13, 'rot': 35, 'shape': 'taper'},
    {'name': 'Central African Savannah', 'cx': 540, 'cy': 397, 'rx': 13, 'ry': 12, 'rot': 0, 'green': True},
    {'name': 'Congo Basin Rainforest', 'cx': 576, 'cy': 408, 'rx': 21, 'ry': 17, 'rot': 5, 'green': True},
    {'name': 'East Africa Rift and Lakes', 'cx': 619, 'cy': 410, 'rx': 17, 'ry': 19, 'rot': 10, 'green': True},
    {'name': 'Angola Atlantic Coast', 'cx': 540, 'cy': 450, 'rx': 13, 'ry': 18, 'rot': -15, 'shape': 'arc'},
    {'name': 'Zambia and Zimbabwe Plateau', 'cx': 582, 'cy': 456, 'rx': 17, 'ry': 15, 'rot': 5},
    {'name': 'Mozambique Channel Coast', 'cx': 622, 'cy': 460, 'rx': 12, 'ry': 18, 'rot': -15, 'shape': 'arc', 'green': True},
    {'name': 'Namibia and Kalahari', 'cx': 556, 'cy': 496, 'rx': 14, 'ry': 16, 'rot': -5},
    {'name': 'South Africa Cape', 'cx': 594, 'cy': 512, 'rx': 19, 'ry': 15, 'rot': 5, 'shape': 'taper'},
    {'name': 'Madagascar Island', 'cx': 664, 'cy': 472, 'rx': 11, 'ry': 22, 'rot': -20, 'green': True},

    # === ASIA AND MIDDLE EAST (35 Islands: Russia, Urals, Siberia, Baikal, Kamchatka, Levant, Arabia, Central Asia, Kazakhstan, Pamir, Iran, India, Tibet, China, Korea, Japan, Indochina, Indonesia) ===
    {'name': 'European Russia Core', 'cx': 671, 'cy': 156, 'rx': 20, 'ry': 16, 'rot': 5, 'green': True},
    {'name': 'Ural Mountains and West Siberia', 'cx': 718, 'cy': 142, 'rx': 25, 'ry': 16, 'rot': 0},
    {'name': 'Central Siberia Plateau', 'cx': 777, 'cy': 131, 'rx': 30, 'ry': 16, 'rot': 0},
    {'name': 'Lake Baikal and Sayan Range', 'cx': 825, 'cy': 142, 'rx': 16, 'ry': 12, 'rot': -5, 'green': True},
    {'name': 'East Siberia and Yakutia', 'cx': 868, 'cy': 130, 'rx': 27, 'ry': 16, 'rot': -5},
    {'name': 'Kamchatka and Bering Shore', 'cx': 926, 'cy': 141, 'rx': 13, 'ry': 16, 'rot': 25, 'shape': 'arc'},
    {'name': 'Sakhalin Island Arc', 'cx': 948, 'cy': 163, 'rx': 7, 'ry': 13, 'rot': 10, 'shape': 'arc'},
    {'name': 'Levant and Mesopotamia', 'cx': 662, 'cy': 270, 'rx': 15, 'ry': 12, 'rot': 15},
    {'name': 'Arabian Peninsula', 'cx': 670, 'cy': 312, 'rx': 20, 'ry': 16, 'rot': -25},
    {'name': 'Central Asian Steppes', 'cx': 724, 'cy': 198, 'rx': 20, 'ry': 14, 'rot': 5},
    {'name': 'Kazakhstan and Altai Steppes', 'cx': 766, 'cy': 185, 'rx': 18, 'ry': 13, 'rot': 10},
    {'name': 'Pamir and Hindu Kush Plateau', 'cx': 752, 'cy': 234, 'rx': 16, 'ry': 13, 'rot': 25},
    {'name': 'Persian Plateau', 'cx': 712, 'cy': 256, 'rx': 17, 'ry': 14, 'rot': 20},
    {'name': 'Pakistan and Indus Basin', 'cx': 745, 'cy': 278, 'rx': 14, 'ry': 15, 'rot': 20},
    {'name': 'Northern India and Himalayas', 'cx': 782, 'cy': 264, 'rx': 19, 'ry': 13, 'rot': 15},
    {'name': 'Bengal and Ganges Delta', 'cx': 816, 'cy': 288, 'rx': 14, 'ry': 14, 'rot': 15, 'green': True},
    {'name': 'Indian Peninsula Triangle', 'cx': 776, 'cy': 318, 'rx': 20, 'ry': 24, 'rot': 15, 'green': True, 'shape': 'taper'},
    {'name': 'Sri Lanka Pearl', 'cx': 792, 'cy': 366, 'rx': 7, 'ry': 9, 'rot': 10},
    {'name': 'Mongolia Steppes', 'cx': 807, 'cy': 179, 'rx': 23, 'ry': 13, 'rot': 0},
    {'name': 'Tibetan High Plateau', 'cx': 816, 'cy': 226, 'rx': 20, 'ry': 12, 'rot': 10},
    {'name': 'Manchuria and Amur River Basin', 'cx': 886, 'cy': 174, 'rx': 17, 'ry': 13, 'rot': 10, 'green': True},
    {'name': 'North China Core', 'cx': 855, 'cy': 201, 'rx': 21, 'ry': 16, 'rot': 5, 'green': True, 'hub': 'asia'},
    {'name': 'East China Coast and Shanghai', 'cx': 895, 'cy': 240, 'rx': 13, 'ry': 14, 'rot': 15, 'green': True},
    {'name': 'South China and Yangtze', 'cx': 860, 'cy': 252, 'rx': 20, 'ry': 16, 'rot': 0, 'green': True},
    {'name': 'Korean Peninsula', 'cx': 908, 'cy': 210, 'rx': 9, 'ry': 15, 'rot': 20},
    {'name': 'Japan Hokkaido', 'cx': 948, 'cy': 192, 'rx': 11, 'ry': 11, 'rot': -20},
    {'name': 'Japan Honshu Arc', 'cx': 954, 'cy': 229, 'rx': 10, 'ry': 22, 'rot': 35, 'shape': 'arc'},
    {'name': 'Taiwan Island', 'cx': 908, 'cy': 272, 'rx': 7, 'ry': 12, 'rot': 25, 'shape': 'arc'},
    {'name': 'Indochina Peninsula Vietnam/Thailand', 'cx': 854, 'cy': 298, 'rx': 16, 'ry': 16, 'rot': 15},
    {'name': 'Malay Peninsula', 'cx': 846, 'cy': 336, 'rx': 8, 'ry': 13, 'rot': 15, 'shape': 'arc'},
    {'name': 'Sumatra Island', 'cx': 836, 'cy': 372, 'rx': 11, 'ry': 18, 'rot': -35, 'green': True, 'shape': 'arc'},
    {'name': 'Java Island', 'cx': 878, 'cy': 392, 'rx': 18, 'ry': 7, 'rot': 5, 'green': True},
    {'name': 'Borneo Heart', 'cx': 892, 'cy': 346, 'rx': 16, 'ry': 15, 'rot': 10, 'green': True},
    {'name': 'Sulawesi and Moluccas', 'cx': 924, 'cy': 358, 'rx': 11, 'ry': 14, 'rot': 25, 'shape': 'arc', 'green': True},
    {'name': 'Philippines Archipelago', 'cx': 932, 'cy': 310, 'rx': 10, 'ry': 16, 'rot': 20},

    # === OCEANIA (12 Islands: Papua New Guinea, Australia Outback, Queensland Reef, Central Australia, New South Wales, Tasmania, New Zealand) ===
    {'name': 'Papua New Guinea', 'cx': 948, 'cy': 386, 'rx': 20, 'ry': 10, 'rot': -10},
    {'name': 'Solomon Islands and Coral Archipelago', 'cx': 996, 'cy': 396, 'rx': 14, 'ry': 8, 'rot': -20},
    {'name': 'Western Australia Outback', 'cx': 884, 'cy': 456, 'rx': 18, 'ry': 20, 'rot': 10},
    {'name': 'Northern Territory Australia', 'cx': 924, 'cy': 432, 'rx': 16, 'ry': 14, 'rot': -5},
    {'name': 'Queensland and Barrier Reef', 'cx': 966, 'cy': 442, 'rx': 14, 'ry': 18, 'rot': -25, 'shape': 'arc', 'green': True},
    {'name': 'Central and South Australia', 'cx': 924, 'cy': 478, 'rx': 20, 'ry': 16, 'rot': 0, 'green': True, 'hub': 'oc'},
    {'name': 'Great Australian Bight and Adelaide', 'cx': 892, 'cy': 497, 'rx': 14, 'ry': 12, 'rot': 15, 'green': True},
    {'name': 'New South Wales and Victoria', 'cx': 964, 'cy': 488, 'rx': 16, 'ry': 16, 'rot': 20, 'green': True},
    {'name': 'Tasmania', 'cx': 960, 'cy': 530, 'rx': 9, 'ry': 7, 'rot': 0},
    {'name': 'New Zealand North Island', 'cx': 1018, 'cy': 482, 'rx': 9, 'ry': 13, 'rot': -35, 'shape': 'arc'},
    {'name': 'New Zealand South Island', 'cx': 992, 'cy': 507, 'rx': 9, 'ry': 15, 'rot': -30, 'shape': 'arc'},
    {'name': 'South Pacific Coral Isles', 'cx': 1038, 'cy': 428, 'rx': 9, 'ry': 7, 'rot': 20},

    # === ANTARCTICA (9 Islands: Antarctic Peninsula, Weddell Sea, Polar Dome Hub, Wilkes, Ross Shelves, Marie Byrd Land) ===
    {'name': 'Ellsworth Land Ice Shelf', 'cx': 349, 'cy': 582, 'rx': 17, 'ry': 9, 'rot': 10, 'sand_light': True},
    {'name': 'Antarctic Peninsula Graham Land', 'cx': 396, 'cy': 592, 'rx': 9, 'ry': 15, 'rot': -35, 'shape': 'arc', 'sand_light': True},
    {'name': 'Weddell Sea Ice Shelf', 'cx': 446, 'cy': 602, 'rx': 22, 'ry': 11, 'sand_light': True},
    {'name': 'Queen Maud Land Shelf', 'cx': 516, 'cy': 602, 'rx': 24, 'ry': 12, 'sand_light': True},
    {'name': 'Antarctic Polar Dome Hub', 'cx': 595, 'cy': 595, 'rx': 25, 'ry': 13, 'sand_light': True, 'hub': 'an'},
    {'name': 'Wilkes Land Ice Shelf', 'cx': 674, 'cy': 602, 'rx': 24, 'ry': 12, 'sand_light': True},
    {'name': 'Ross Ice Shelf East', 'cx': 748, 'cy': 602, 'rx': 24, 'ry': 11, 'sand_light': True},
    {'name': 'Ross Sea Ice Shelf West', 'cx': 812, 'cy': 592, 'rx': 20, 'ry': 11, 'sand_light': True},
    {'name': 'Marie Byrd Land Shelf', 'cx': 864, 'cy': 576, 'rx': 18, 'ry': 11, 'rot': -10, 'sand_light': True},
]

# Inter-island footbridges
bridges = [
        # --- North America ---
        ((286, 224), (331, 214)),  # US Rocky Mountains and Plains to US Midwest and Great Lakes
        ((308, 174), (331, 214)),  # Canadian Shield Ontario to US Midwest and Great Lakes
        ((331, 214), (361, 164)),  # US Midwest and Great Lakes to Quebec and Labrador
        ((361, 164), (359, 123)),  # Quebec and Labrador to Baffin Island
        ((331, 214), (374, 212)),  # US Midwest and Great Lakes to US East Coast and New England
        ((331, 214), (342, 256)),  # US Midwest and Great Lakes to US South and Gulf Coast
        ((342, 256), (382, 268)),  # US South and Gulf Coast to Florida Peninsula
        ((286, 224), (298, 260)),  # US Rocky Mountains and Plains to Texas and Southern Great Plains
        ((298, 260), (278, 296)),  # Texas and Southern Great Plains to Northern Mexico
        ((278, 296), (298, 328)),  # Northern Mexico to Southern Mexico
        ((298, 328), (338, 318)),  # Southern Mexico to Yucatan Peninsula
        ((298, 328), (328, 352)),  # Southern Mexico to Central America Isthmus
        ((361, 164), (404, 178)),  # Quebec and Labrador to Newfoundland and Maritimes

        # --- South America ---
        ((354, 382), (390, 370)),  # Colombia and Northern Andes to Venezuela and Orinoco
        ((354, 382), (386, 409)),  # Colombia and Northern Andes to Amazon Basin Heart
        ((342, 420), (386, 409)),  # Peru and Central Andes to Amazon Basin Heart
        ((390, 370), (424, 378)),  # Venezuela and Orinoco to Guyana Coast
        ((386, 409), (380, 448)),  # Amazon Basin Heart to Bolivia and Pantanal
        ((386, 409), (447, 415)),  # Amazon Basin Heart to Brazil Northeast Bulge
        ((386, 409), (415, 438)),  # Amazon Basin Heart to Central Brazil and Cerrado Plateau
        ((415, 438), (436, 469)),  # Central Brazil and Cerrado Plateau to Brazil Southeast Coast
        ((380, 448), (366, 479)),  # Bolivia and Pantanal to Paraguay and Gran Chaco Basin
        ((338, 489), (366, 479)),  # Chile Andes Strip to Paraguay and Gran Chaco Basin
        ((366, 479), (385, 512)),  # Paraguay and Gran Chaco Basin to Argentina Pampas Core
        ((385, 512), (418, 505)),  # Argentina Pampas Core to Uruguay and Rio de la Plata
        ((385, 512), (369, 547)),  # Argentina Pampas Core to Patagonia Southern Wedge
        ((369, 547), (379, 572)),  # Patagonia Southern Wedge to Tierra del Fuego
        ((379, 572), (402, 565)),  # Tierra del Fuego to Falkland Islands

        # --- Europe ---
        ((498, 176), (524, 166)),  # Ireland to Great Britain
        ((524, 166), (544, 214)),  # Great Britain to Western Europe Mainland Core
        ((544, 214), (513, 230)),  # Western Europe Mainland Core to France and Biscay Bay
        ((513, 230), (500, 260)),  # France and Biscay Bay to Iberian Peninsula
        ((544, 214), (582, 204)),  # Western Europe Mainland Core to Central Europe Germany and Alps
        ((582, 204), (564, 168)),  # Central Europe Germany and Alps to Denmark and Jutland Peninsula
        ((564, 168), (592, 134)),  # Denmark and Jutland Peninsula to Sweden and Finland
        ((564, 168), (558, 130)),  # Denmark and Jutland Peninsula to Norway Fjord Coast
        ((582, 204), (615, 225)),  # Central Europe Germany and Alps to Danube Basin and Romania
        ((582, 204), (618, 178)),  # Central Europe Germany and Alps to Poland and Baltic States
        ((615, 225), (647, 210)),  # Danube Basin and Romania to Eastern Europe Ukraine Plains
        ((618, 178), (647, 210)),  # Poland and Baltic States to Eastern Europe Ukraine Plains

        # --- Africa ---
        ((503, 320), (540, 326)),  # Morocco and Atlas to Sahara Core Northwest
        ((540, 326), (581, 326)),  # Sahara Core Northwest to Libya and Central Sahara
        ((581, 326), (622, 318)),  # Libya and Central Sahara to Egypt and Nile Delta
        ((514, 368), (558, 364)),  # Gulf of Guinea Ivory Coast to Nigeria and Sahel
        ((558, 364), (581, 326)),  # Nigeria and Sahel to Libya and Central Sahara
        ((558, 364), (616, 362)),  # Nigeria and Sahel to Sudan and Nubia Basin
        ((558, 364), (576, 408)),  # Nigeria and Sahel to Congo Basin Rainforest
        ((576, 408), (619, 410)),  # Congo Basin Rainforest to East Africa Rift and Lakes
        ((576, 408), (582, 456)),  # Congo Basin Rainforest to Zambia and Zimbabwe Plateau
        ((582, 456), (622, 460)),  # Zambia and Zimbabwe Plateau to Mozambique Channel Coast
        ((582, 456), (594, 512)),  # Zambia and Zimbabwe Plateau to South Africa Cape

        # --- Asia ---
        ((671, 156), (718, 142)),  # European Russia Core to Ural Mountains and West Siberia
        ((718, 142), (777, 131)),  # Ural Mountains and West Siberia to Central Siberia Plateau
        ((777, 131), (825, 142)),  # Central Siberia Plateau to Lake Baikal and Sayan Range
        ((825, 142), (868, 130)),  # Lake Baikal and Sayan Range to East Siberia and Yakutia
        ((825, 142), (807, 179)),  # Lake Baikal and Sayan Range to Mongolia Steppes
        ((718, 142), (724, 198)),  # Ural Mountains to Central Asian Steppes
        ((724, 198), (766, 185)),  # Central Asian Steppes to Kazakhstan and Altai Steppes
        ((766, 185), (807, 179)),  # Kazakhstan and Altai Steppes to Mongolia Steppes
        ((766, 185), (777, 131)),  # Kazakhstan and Altai Steppes to Central Siberia Plateau
        ((724, 198), (752, 234)),  # Central Asian Steppes to Pamir and Hindu Kush Plateau
        ((752, 234), (782, 264)),  # Pamir and Hindu Kush Plateau to Northern India and Himalayas
        ((752, 234), (745, 278)),  # Pamir and Hindu Kush Plateau to Pakistan and Indus Basin
        ((712, 256), (752, 234)),  # Persian Plateau to Pamir and Hindu Kush Plateau
        ((752, 234), (816, 226)),  # Pamir and Hindu Kush Plateau to Tibetan High Plateau
        ((807, 179), (855, 201)),  # Mongolia Steppes to North China Core
        ((816, 226), (855, 201)),  # Tibetan High Plateau to North China Core
        ((855, 201), (886, 174)),  # North China Core to Manchuria and Amur River Basin
        ((855, 201), (908, 210)),  # North China Core to Korean Peninsula
        ((855, 201), (895, 240)),  # North China Core to East China Coast and Shanghai
        ((855, 201), (860, 252)),  # North China Core to South China and Yangtze
        ((860, 252), (854, 298)),  # South China and Yangtze to Indochina Peninsula Vietnam/Thailand
        ((782, 264), (816, 288)),  # Northern India and Himalayas to Bengal and Ganges Delta
        ((816, 288), (854, 298)),  # Bengal and Ganges Delta to Indochina Peninsula Vietnam/Thailand
        ((854, 298), (846, 336)),  # Indochina Peninsula Vietnam/Thailand to Malay Peninsula
        ((892, 346), (854, 298)),  # Borneo Heart to Indochina Peninsula Vietnam/Thailand
        ((892, 346), (924, 358)),  # Borneo Heart to Sulawesi and Moluccas

        # --- Oceania ---
        ((884, 456), (924, 478)),  # Western Australia Outback to Central and South Australia
        ((924, 432), (924, 478)),  # Northern Territory Australia to Central and South Australia
        ((924, 478), (966, 442)),  # Central and South Australia to Queensland and Barrier Reef
        ((924, 478), (892, 497)),  # Central and South Australia to Great Australian Bight and Adelaide
        ((924, 478), (964, 488)),  # Central and South Australia to New South Wales and Victoria
        ((964, 488), (960, 530)),  # New South Wales and Victoria to Tasmania (Bass Strait Bridge)
        ((1018, 482), (992, 507)),  # New Zealand North Island to New Zealand South Island

        # --- Antarctica Chain ---
        ((349, 582), (396, 592)),  # Ellsworth Land to Antarctic Peninsula Graham Land
        ((396, 592), (446, 602)),  # Antarctic Peninsula Graham Land to Weddell Sea Ice Shelf
        ((446, 602), (516, 602)),  # Weddell Sea Ice Shelf to Queen Maud Land Shelf
        ((516, 602), (595, 595)),  # Queen Maud Land Shelf to Antarctic Polar Dome Hub

        # ==================== INTER-CONTINENTAL BRIDGES ====================
        # 1. North America <-> South America & Caribbean
        ((328, 352), (354, 382)),  # Central America Isthmus to Colombia and Northern Andes (Panama Bridge)
        ((382, 268), (398, 304)),  # Florida Peninsula to Cuba and Greater Antilles
        ((398, 304), (424, 322)),  # Cuba and Greater Antilles to Bahamas and Caribbean Chain

        # 2. Europe <-> Africa
        ((564, 260), (562, 288)),  # Italy Boot Peninsula to Sicily and Malta
        ((562, 288), (581, 326)),  # Sicily and Malta to Libya and Central Sahara

        # 3. Africa <-> Asia & Middle East
        ((622, 318), (670, 312)),  # Egypt and Nile Delta to Arabian Peninsula (Sinai/Red Sea Bridge)
        ((622, 318), (662, 270)),  # Egypt and Nile Delta to Levant and Mesopotamia (Suez Bridge)
        ((658, 366), (670, 312)),  # Horn of Africa Somalia to Arabian Peninsula (Bab-el-Mandeb Strait Bridge)

        # 4. Europe <-> Asia
        ((602, 256), (662, 270)),  # Balkans and Greece to Levant and Mesopotamia (Bosphorus Bridge)
        ((647, 210), (662, 270)),  # Eastern Europe Ukraine Plains to Levant and Mesopotamia (Caucasus Bridge)
        ((647, 210), (671, 156)),  # Eastern Europe Ukraine Plains to European Russia Core
        ((618, 178), (671, 156)),  # Poland and Baltic States to European Russia Core
        ((662, 270), (712, 256)),  # Levant and Mesopotamia to Persian Plateau
        ((712, 256), (745, 278)),  # Persian Plateau to Pakistan and Indus Basin
        ((745, 278), (782, 264)),  # Pakistan and Indus Basin to Northern India and Himalayas

        # 5. Asia <-> Oceania & Australia
        ((846, 336), (836, 372)),  # Malay Peninsula to Sumatra Island (Malacca Strait Bridge)
        ((836, 372), (878, 392)),  # Sumatra Island to Java Island (Sunda Strait Bridge)
        ((878, 392), (892, 346)),  # Java Island to Borneo Heart
        ((924, 358), (948, 386)),  # Sulawesi and Moluccas to Papua New Guinea
        ((948, 386), (924, 432)),  # Papua New Guinea to Northern Territory Australia (Arafura Sea Bridge)
        ((948, 386), (996, 396)),  # Papua New Guinea to Solomon Islands

        # 6. South America <-> Antarctica
        ((379, 572), (396, 592)),  # Tierra del Fuego to Antarctic Peninsula Graham Land (Drake Passage Bridge)

        # 7. North America <-> Europe (Stepping Stones)
        ((359, 123), (424, 112)),  # Baffin Island to Greenland Isle
        ((494, 128), (524, 166)),  # Iceland to Great Britain
]

def world_svg():
    ecx, ecy, erx, ery = 600, 345, 540, 305
    o = map_header()
    o += [
        "<!-- Lagoon Shallows -->",
        f'<ellipse cx="{ecx}" cy="{ecy}" rx="{erx}" ry="{ery}" fill="url(#lagoon-glow)" />',
        "<!-- Wave Break Line -->",
        f'<ellipse cx="{ecx}" cy="{ecy}" rx="{erx + 25}" ry="{ery + 23}" fill="none" stroke="rgba(255,255,255,0.14)" stroke-dasharray="6 8" />',
    ]

    # Oval flood defense breakwater (4 storm gates: N, S, E, W)
    arcs = []
    gap = 5
    for start in (0, 90, 180, 270):
        a = math.radians(start + gap)
        b = math.radians(start + 90 - gap)
        pa = (ecx + erx * math.cos(a), ecy + ery * math.sin(a))
        pb = (ecx + erx * math.cos(b), ecy + ery * math.sin(b))
        arcs.append(f"M{pt(pa)} A{erx},{ery} 0 0 1 {pt(pb)}")
    ring = " ".join(arcs)
    o += [
        "<!-- Outer Oval Flood Defense Breakwater (4 Storm Gates: N, S, E, W) -->",
        f'<path d="{ring}" fill="none" stroke="#2ba29e" stroke-width="26" stroke-linecap="round" opacity="0.45" />',
        f'<path class="map-frond-edge" d="{ring}" stroke-width="15" />',
        f'<path class="map-frond" d="{ring}" stroke-width="12.5" />',
    ]

    # Gate beacons
    o.append('<g class="twinkle">')
    for start in (0, 90, 180, 270):
        for s, col in ((-1, "#ef4444"), (1, "#22c55e")):
            a = math.radians(start + s * gap)
            o.append(f'<circle cx="{n(ecx + erx * math.cos(a))}" cy="{n(ecy + ery * math.sin(a))}" r="3.5" fill="{col}" />')
    o.append("</g>")

    # MULTIPLE ISLANDS
    o.append("<!-- RECOGNIZABLE WORLD CONTINENTS (VARIED SHAPES, ZERO OVERLAPS) -->")
    o.append('<g id="world-islands-group">')
    for i, isle in enumerate(WORLD_ISLES):
        cls = "map-sand-light" if isle.get("sand_light") else "map-sand"
        shape = isle.get("shape", "organic")
        d = smooth_island(isle["cx"], isle["cy"], isle["rx"], isle["ry"], rot=isle.get("rot", 0), seed=i + 1, shape=shape)
        o.append(f'<!-- {isle["name"]} -->')
        o.append(f'<path class="{cls}" d="{d}" />')
        if isle.get("green"):
            d_grn = smooth_island(isle["cx"], isle["cy"], isle["rx"] * 0.65, isle["ry"] * 0.65, rot=isle.get("rot", 0), seed=i + 10, shape=shape)
            o.append(f'<path class="map-greenery" d="{d_grn}" />')
    o.append("</g>")

    # Hub architectures on main continental islands
    us_hub = (331, 214)
    eu_hub = (544, 214)
    asia_hub = (855, 201)
    oc_hub = (924, 478)
    an_hub = (595, 595)

    o += [
        "<!-- Continental Hub Pavilions and Features -->",
        f'<rect x="{us_hub[0] - 16}" y="{us_hub[1] - 9}" width="32" height="18" rx="3" class="map-urban" />',
        f'<rect x="{eu_hub[0] - 14}" y="{eu_hub[1] - 8}" width="28" height="16" rx="3" class="map-urban" />',
        f'<rect x="{asia_hub[0] - 18}" y="{asia_hub[1] - 9}" width="36" height="18" rx="3" class="map-urban" />',
        f'<ellipse cx="{an_hub[0]}" cy="{an_hub[1]}" rx="24" ry="9" fill="#38bdf8" stroke="#ffffff" stroke-width="1.6" opacity="0.85" />',
    ]

    o.append("<!-- Inter-Island Arched Footbridges -->")
    o.append('<g stroke="#ffffff" stroke-width="2.2" stroke-linecap="round">')
    for b1, b2 in bridges:
        o.append(f'<line x1="{n(b1[0])}" y1="{n(b1[1])}" x2="{n(b2[0])}" y2="{n(b2[1])}" />')
    o.append("</g>")

    # Continental Cable Car
    tele_path = [us_hub, eu_hub]
    o += [
        "<!-- Continental Cable Car -->",
        f'<path class="map-cableway" d="{poly_path(tele_path, close=False)}" />',
    ]
    for p in tele_path:
        o.append(f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="5" fill="#f43f5e" stroke="#ffffff" stroke-width="1.8" />')

    # Submerged suites in coral lagoon
    sub_suites = (695, 405)
    o += ["<!-- Submerged Reef Observation Suites -->"]
    for ddx, ddy in ((-12, -10), (14, 12)):
        o += [
            f'<g transform="translate({sub_suites[0] + ddx}, {sub_suites[1] + ddy})">',
            '<circle cx="0" cy="0" r="7" fill="#0284c7" stroke="#38bdf8" stroke-width="2" />',
            '<circle cx="0" cy="0" r="2.6" fill="#ffffff" class="twinkle" />',
            "</g>",
        ]
    
    # 8 Interactive Hotspots
    tele_mid = ((eu_hub[0] + asia_hub[0]) / 2, (eu_hub[1] + asia_hub[1]) / 2)
    spots = [
        (1, us_hub[0], us_hub[1], "#f43f5e", "NA Casino and Theme Park"),
        (2, eu_hub[0], eu_hub[1], "#c29a57", "European Summit and Diplomatic Pavilions"),
        (3, asia_hub[0], asia_hub[1], "#38bdf8", "Asian Innovation Hub"),
        (4, tele_mid[0], tele_mid[1], "#f43f5e", "Continental Teleferic"),
        (5, sub_suites[0], sub_suites[1], "#0284c7", "Submerged Reef Suites"),
        (6, an_hub[0], an_hub[1], "#38bdf8", "Antarctic Climate Dome"),
        (7, oc_hub[0], oc_hub[1], "#22c55e", "Oceania Dolphin Sanctuary"),
        (8, ecx, ecy - ery, "#2ba29e", "Flood Barrier Storm Gates"),
    ]
    o.append("<!-- INTERACTIVE HOTSPOT PINS -->")
    for i, x, y, col, name in spots:
        o.append(f"<!-- Hotspot {i}: {name} -->")
        o += hotspot(i, x, y, col)
    o.append("</svg>")
    return o

def main():
    update_island_map(1, world_svg)

if __name__ == "__main__":
    main()