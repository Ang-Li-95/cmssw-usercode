import sys
from array import array
from collections import defaultdict

tau0s = [100*x for x in xrange(1,10)] + [1000*x for x in range(1,11) + range(12,43,2)]
masses = range(300, 1501, 100)

ntau0s = len(tau0s)
nmasses = len(masses)

def make_name(tau0, mass):
    return 'mfv_neutralino_tau%05ium_M%04i' % (tau0, mass)

num2tau = {}
num2mass = {}
name2num = {}
num2name = {}
name2mass = {}
name2fn = {}
num2nevt = {}
num2npass = {
    0: {-555: 44636, -554: 44081, -553: 43079, -552: 44086, -551: 43413, -550: 42952, -549: 42075, -548: 40826, -547: 39167, -546: 37348, -545: 33793, -544: 26213, -543: 11464, -542: 45180, -541: 44843, -540: 44529, -539: 44953, -538: 44054, -537: 44273, -536: 43238, -535: 42064, -534: 40580, -533: 38679, -532: 35008, -531: 27336, -530: 12299, -529: 46601, -528: 46875, -527: 46874, -526: 46435, -525: 46352, -524: 45455, -523: 44866, -522: 43724, -521: 42262, -520: 39688, -519: 36685, -518: 28589, -517: 12734, -516: 47290, -515: 48176, -514: 48020, -513: 48048, -512: 47924, -511: 47050, -510: 46654, -509: 45342, -508: 43493, -507: 41491, -506: 37971, -505: 29810, -504: 13213, -503: 49651, -502: 49625, -501: 49269, -500: 49318, -499: 49403, -498: 48694, -497: 48111, -496: 46982, -495: 45078, -494: 43290, -493: 39565, -492: 31232, -491: 14135, -490: 50814, -489: 51053, -488: 50617, -487: 50995, -486: 51001, -485: 50127, -484: 49679, -483: 48551, -482: 46965, -481: 44536, -480: 40870, -479: 32435, -478: 14863, -477: 52008, -476: 52175, -475: 52193, -474: 52603, -473: 52738, -472: 51948, -471: 51093, -470: 50243, -469: 48630, -468: 46759, -467: 42995, -466: 33938, -465: 15798, -464: 53179, -463: 53797, -462: 54140, -461: 53963, -460: 53865, -459: 53744, -458: 52898, -457: 52070, -456: 50757, -455: 48613, -454: 44625, -453: 35287, -452: 16623, -451: 54790, -450: 55164, -449: 55306, -448: 55364, -447: 55806, -446: 55186, -445: 54993, -444: 53650, -443: 52707, -442: 50417, -441: 46192, -440: 37248, -439: 17713, -438: 55922, -437: 56673, -436: 56721, -435: 56961, -434: 57251, -433: 57202, -432: 56486, -431: 55543, -430: 54112, -429: 52296, -428: 48060, -427: 38860, -426: 18416, -425: 57281, -424: 57760, -423: 58282, -422: 58650, -421: 58548, -420: 58612, -419: 58208, -418: 57334, -417: 56493, -416: 54532, -415: 50263, -414: 40501, -413: 19472, -412: 58332, -411: 59365, -410: 59779, -409: 59151, -408: 60372, -407: 60148, -406: 59895, -405: 59817, -404: 58547, -403: 56578, -402: 52204, -401: 42339, -400: 20640, -399: 59499, -398: 60353, -397: 60701, -396: 61428, -395: 61412, -394: 61979, -393: 61958, -392: 61264, -391: 60039, -390: 58526, -389: 54069, -388: 43973, -387: 22026, -386: 60032, -385: 61228, -384: 61996, -383: 62470, -382: 62685, -381: 63430, -380: 63423, -379: 62970, -378: 62374, -377: 60140, -376: 56380, -375: 45958, -374: 23176, -373: 61210, -372: 61648, -371: 62512, -370: 63476, -369: 64103, -368: 64755, -367: 64596, -366: 64466, -365: 63815, -364: 62335, -363: 57858, -362: 47459, -361: 24499, -360: 61586, -359: 62185, -358: 63085, -357: 63883, -356: 64911, -355: 65076, -354: 65921, -353: 65585, -352: 65127, -351: 63214, -350: 59202, -349: 49209, -348: 25300, -347: 61219, -346: 62257, -345: 63537, -344: 64037, -343: 64743, -342: 65691, -341: 66243, -340: 66346, -339: 65866, -338: 64290, -337: 60210, -336: 49410, -335: 26560, -334: 61115, -333: 61789, -332: 62559, -331: 63565, -330: 64735, -329: 65587, -328: 66249, -327: 66548, -326: 65856, -325: 64428, -324: 60643, -323: 49935, -322: 26597, -321: 60456, -320: 61456, -319: 61978, -318: 63133, -317: 64152, -316: 64804, -315: 65840, -314: 65887, -313: 65834, -312: 64460, -311: 60159, -310: 49898, -309: 26832, -308: 59429, -307: 60550, -306: 61475, -305: 62541, -304: 63392, -303: 64120, -302: 64934, -301: 65654, -300: 65011, -299: 63974, -298: 59968, -297: 49490, -296: 26222, -295: 58537, -294: 59267, -293: 60163, -292: 60825, -291: 62108, -290: 63052, -289: 63759, -288: 64206, -287: 64001, -286: 62641, -285: 58895, -284: 48393, -283: 26232, -282: 56612, -281: 57897, -280: 58492, -279: 59776, -278: 60496, -277: 61422, -276: 62063, -275: 62526, -274: 62457, -273: 61039, -272: 57133, -271: 47533, -270: 25410, -269: 54136, -268: 55493, -267: 56212, -266: 57472, -265: 58213, -264: 58935, -263: 59734, -262: 59823, -261: 59564, -260: 58402, -259: 54696, -258: 44745, -257: 24182, -256: 50326, -255: 51489, -254: 51989, -253: 53100, -252: 54100, -251: 54769, -250: 55558, -249: 56042, -248: 55568, -247: 54159, -246: 50480, -245: 41697, -244: 22034, -243: 44436, -242: 45055, -241: 46098, -240: 46915, -239: 47076, -238: 48364, -237: 48942, -236: 49494, -235: 49012, -234: 47290, -233: 43875, -232: 35687, -231: 18914, -230: 31880, -229: 32497, -228: 33122, -227: 33713, -226: 34361, -225: 35179, -224: 35502, -223: 35926, -222: 35295, -221: 33973, -220: 31579, -219: 25118, -218: 13317, -217: 29819, -216: 30383, -215: 30921, -214: 31848, -213: 32400, -212: 33248, -211: 33370, -210: 33803, -209: 33373, -208: 31784, -207: 29091, -206: 23447, -205: 12344, -204: 27651, -203: 28298, -202: 28766, -201: 29113, -200: 29604, -199: 30663, -198: 31069, -197: 31296, -196: 30620, -195: 29807, -194: 26962, -193: 21426, -192: 11103, -191: 25052, -190: 25590, -189: 25943, -188: 26486, -187: 27272, -186: 27947, -185: 28431, -184: 28310, -183: 28287, -182: 27027, -181: 24248, -180: 19398, -179: 10249, -178: 21944, -177: 22529, -176: 23055, -175: 23672, -174: 24301, -173: 24570, -172: 25197, -171: 25257, -170: 24991, -169: 23968, -168: 21614, -167: 17068, -166: 9195, -165: 18678, -164: 19192, -163: 20032, -162: 20347, -161: 20612, -160: 21175, -159: 21698, -158: 21729, -157: 21632, -156: 20630, -155: 18514, -154: 14691, -153: 7777, -152: 14744, -151: 15356, -150: 15621, -149: 16506, -148: 16739, -147: 17197, -146: 17380, -145: 17688, -144: 17143, -143: 16511, -142: 14689, -141: 11650, -140: 6073, -139: 10434, -138: 10912, -137: 11508, -136: 11595, -135: 12136, -134: 12743, -133: 12713, -132: 12810, -131: 12632, -130: 11993, -129: 10764, -128: 8223, -127: 4438, -126: 5697, -125: 5971, -124: 6193, -123: 6478, -122: 6961, -121: 7056, -120: 7101, -119: 7298, -118: 7223, -117: 6814, -116: 5968, -115: 4580, -114: 2590, -113: 1461, -112: 1489, -111: 1622, -110: 1644, -109: 1753, -108: 1916, -107: 1965, -106: 1846, -105: 1976, -104: 1748, -103: 1570, -102: 1241, -101: 670},
    600: {-555: 43030, -554: 42485, -553: 41486, -552: 42493, -551: 41845, -550: 41398, -549: 40545, -548: 39335, -547: 37742, -546: 36049, -545: 32725, -544: 25507, -543: 11164, -542: 43527, -541: 43209, -540: 42965, -539: 43332, -538: 42451, -537: 42647, -536: 41749, -535: 40557, -534: 39211, -533: 37448, -532: 33934, -531: 26636, -530: 11973, -529: 45049, -528: 45316, -527: 45295, -526: 44886, -525: 44728, -524: 43856, -523: 43362, -522: 42292, -521: 40888, -520: 38426, -519: 35676, -518: 27837, -517: 12453, -516: 45707, -515: 46574, -514: 46343, -513: 46492, -512: 46344, -511: 45457, -510: 45115, -509: 43905, -508: 42160, -507: 40214, -506: 36954, -505: 29067, -504: 12907, -503: 48002, -502: 48005, -501: 47673, -500: 47763, -499: 47794, -498: 47146, -497: 46518, -496: 45554, -495: 43776, -494: 42012, -493: 38518, -492: 30517, -491: 13844, -490: 49220, -489: 49426, -488: 49047, -487: 49382, -486: 49353, -485: 48637, -484: 48189, -483: 47116, -482: 45620, -481: 43393, -480: 39827, -479: 31679, -478: 14555, -477: 50312, -476: 50579, -475: 50525, -474: 51007, -473: 51188, -472: 50390, -471: 49595, -470: 48810, -469: 47272, -468: 45514, -467: 41914, -466: 33207, -465: 15494, -464: 51558, -463: 52075, -462: 52507, -461: 52437, -460: 52352, -459: 52229, -458: 51393, -457: 50621, -456: 49421, -455: 47450, -454: 43577, -453: 34531, -452: 16335, -451: 53035, -450: 53517, -449: 53694, -448: 53716, -447: 54123, -446: 53674, -445: 53452, -444: 52345, -443: 51422, -442: 49238, -441: 45244, -440: 36543, -439: 17416, -438: 54226, -437: 55019, -436: 55098, -435: 55366, -434: 55651, -433: 55634, -432: 55022, -431: 54170, -430: 52821, -429: 51090, -428: 47123, -427: 38138, -426: 18098, -425: 55587, -424: 56106, -423: 56649, -422: 56990, -421: 57013, -420: 57070, -419: 56705, -418: 55963, -417: 55152, -416: 53312, -415: 49269, -414: 39734, -413: 19170, -412: 56578, -411: 57619, -410: 58091, -409: 57557, -408: 58826, -407: 58655, -406: 58381, -405: 58436, -404: 57250, -403: 55418, -402: 51208, -401: 41610, -400: 20341, -399: 57615, -398: 58585, -397: 59032, -396: 59695, -395: 59812, -394: 60410, -393: 60462, -392: 59878, -391: 58775, -390: 57348, -389: 53037, -388: 43247, -387: 21728, -386: 58126, -385: 59388, -384: 60227, -383: 60697, -382: 60982, -381: 61835, -380: 61950, -379: 61542, -378: 61074, -377: 58930, -376: 55318, -375: 45239, -374: 22848, -373: 59089, -372: 59630, -371: 60616, -370: 61610, -369: 62394, -368: 63150, -367: 63052, -366: 63029, -365: 62452, -364: 61112, -363: 56818, -362: 46681, -361: 24168, -360: 59354, -359: 59984, -358: 60997, -357: 61936, -356: 63049, -355: 63222, -354: 64303, -353: 64119, -352: 63720, -351: 61957, -350: 58069, -349: 48402, -348: 24954, -347: 58775, -346: 59770, -345: 61207, -344: 61821, -343: 62625, -342: 63769, -341: 64432, -340: 64756, -339: 64305, -338: 62963, -337: 59068, -336: 48548, -335: 26172, -334: 58391, -333: 59178, -332: 60071, -331: 61274, -330: 62518, -329: 63498, -328: 64371, -327: 64744, -326: 64216, -325: 62943, -324: 59372, -323: 48984, -322: 26239, -321: 57539, -320: 58600, -319: 59307, -318: 60507, -317: 61774, -316: 62557, -315: 63704, -314: 63982, -313: 64052, -312: 62852, -311: 58797, -310: 48926, -309: 26446, -308: 56143, -307: 57355, -306: 58407, -305: 59707, -304: 60714, -303: 61638, -302: 62652, -301: 63607, -300: 63123, -299: 62175, -298: 58529, -297: 48484, -296: 25832, -295: 54918, -294: 55806, -293: 56903, -292: 57728, -291: 59105, -290: 60305, -289: 61126, -288: 61755, -287: 61834, -286: 60704, -285: 57276, -284: 47267, -283: 25775, -282: 52278, -281: 53882, -280: 54601, -279: 55992, -278: 57024, -277: 58350, -276: 59052, -275: 59743, -274: 59862, -273: 58832, -272: 55189, -271: 46232, -270: 24910, -269: 48983, -268: 50539, -267: 51472, -266: 53045, -265: 54050, -264: 55039, -263: 56091, -262: 56628, -261: 56584, -260: 55743, -259: 52449, -258: 43174, -257: 23587, -256: 43937, -255: 45323, -254: 46178, -253: 47551, -252: 48804, -251: 49844, -250: 51096, -249: 51922, -248: 51941, -247: 50782, -246: 47608, -245: 39748, -244: 21331, -243: 35876, -242: 36919, -241: 38352, -240: 39504, -239: 40154, -238: 41650, -237: 42822, -236: 43786, -235: 43784, -234: 42630, -233: 40004, -232: 33163, -231: 17903, -230: 20101, -229: 20952, -228: 22006, -227: 23130, -226: 24129, -225: 25416, -224: 26344, -223: 27347, -222: 27517, -221: 26820, -220: 25694, -219: 20937, -218: 11636, -217: 17715, -216: 18641, -215: 19460, -214: 20868, -213: 21782, -212: 23178, -211: 23907, -210: 24624, -209: 24945, -208: 24489, -207: 22942, -206: 19217, -205: 10523, -204: 15501, -203: 16308, -202: 17116, -201: 17791, -200: 18865, -199: 20296, -198: 21131, -197: 21917, -196: 22107, -195: 22088, -194: 20468, -193: 16905, -192: 9220, -191: 12621, -190: 13700, -189: 14121, -188: 15178, -187: 16226, -186: 17177, -185: 18041, -184: 18793, -183: 19308, -182: 19059, -181: 17577, -180: 14757, -179: 8233, -178: 9937, -177: 10529, -176: 11291, -175: 12208, -174: 13078, -173: 13975, -172: 14719, -171: 15477, -170: 15763, -169: 15663, -168: 14775, -167: 12156, -166: 7035, -165: 7046, -164: 7592, -163: 8654, -162: 9139, -161: 9734, -160: 10466, -159: 11170, -158: 11852, -157: 12324, -156: 12360, -155: 11559, -154: 9681, -153: 5445, -152: 4493, -151: 4898, -150: 5388, -149: 6133, -148: 6415, -147: 7193, -146: 7709, -145: 8186, -144: 8566, -143: 8498, -142: 8180, -141: 6726, -140: 3946, -139: 2162, -138: 2556, -137: 2699, -136: 3076, -135: 3400, -134: 3893, -133: 4144, -132: 4625, -131: 4843, -130: 4945, -129: 4668, -128: 3972, -127: 2421, -126: 561, -125: 677, -124: 750, -123: 918, -122: 1117, -121: 1202, -120: 1397, -119: 1507, -118: 1658, -117: 1755, -116: 1697, -115: 1406, -114: 941, -113: 33, -112: 43, -111: 44, -110: 57, -109: 69, -108: 94, -107: 92, -106: 113, -105: 171, -104: 148, -103: 140, -102: 140, -101: 109},
    800: {-555: 42880, -554: 42338, -553: 41357, -552: 42376, -551: 41747, -550: 41302, -549: 40456, -548: 39235, -547: 37669, -546: 35970, -545: 32666, -544: 25476, -543: 11151, -542: 43387, -541: 43063, -540: 42839, -539: 43210, -538: 42317, -537: 42532, -536: 41634, -535: 40475, -534: 39130, -533: 37366, -532: 33855, -531: 26594, -530: 11959, -529: 44889, -528: 45169, -527: 45126, -526: 44740, -525: 44604, -524: 43722, -523: 43251, -522: 42189, -521: 40780, -520: 38324, -519: 35612, -518: 27792, -517: 12442, -516: 45544, -515: 46415, -514: 46176, -513: 46364, -512: 46197, -511: 45339, -510: 44990, -509: 43785, -508: 42067, -507: 40135, -506: 36880, -505: 29026, -504: 12893, -503: 47811, -502: 47843, -501: 47499, -500: 47597, -499: 47639, -498: 47007, -497: 46385, -496: 45441, -495: 43673, -494: 41921, -493: 38427, -492: 30461, -491: 13825, -490: 49027, -489: 49204, -488: 48877, -487: 49210, -486: 49204, -485: 48492, -484: 48049, -483: 46970, -482: 45505, -481: 43302, -480: 39754, -479: 31618, -478: 14528, -477: 50083, -476: 50363, -475: 50322, -474: 50822, -473: 50994, -472: 50218, -471: 49434, -470: 48668, -469: 47165, -468: 45386, -467: 41821, -466: 33137, -465: 15472, -464: 51301, -463: 51839, -462: 52280, -461: 52226, -460: 52160, -459: 52039, -458: 51236, -457: 50451, -456: 49305, -455: 47332, -454: 43449, -453: 34435, -452: 16311, -451: 52760, -450: 53252, -449: 53444, -448: 53472, -447: 53911, -446: 53483, -445: 53269, -444: 52172, -443: 51288, -442: 49118, -441: 45131, -440: 36461, -439: 17393, -438: 53911, -437: 54748, -436: 54831, -435: 55118, -434: 55403, -433: 55409, -432: 54829, -431: 54007, -430: 52668, -429: 50933, -428: 46997, -427: 38055, -426: 18062, -425: 55225, -424: 55756, -423: 56343, -422: 56729, -421: 56746, -420: 56834, -419: 56492, -418: 55750, -417: 54965, -416: 53164, -415: 49141, -414: 39641, -413: 19144, -412: 56187, -411: 57227, -410: 57709, -409: 57227, -408: 58513, -407: 58387, -406: 58119, -405: 58218, -404: 57059, -403: 55212, -402: 51059, -401: 41508, -400: 20303, -399: 57138, -398: 58181, -397: 58591, -396: 59338, -395: 59495, -394: 60080, -393: 60176, -392: 59626, -391: 58538, -390: 57113, -389: 52838, -388: 43116, -387: 21691, -386: 57642, -385: 58860, -384: 59757, -383: 60270, -382: 60594, -381: 61458, -380: 61599, -379: 61246, -378: 60776, -377: 58654, -376: 55079, -375: 45074, -374: 22804, -373: 58443, -372: 59037, -371: 60066, -370: 61069, -369: 61894, -368: 62678, -367: 62652, -366: 62682, -365: 62156, -364: 60831, -363: 56526, -362: 46512, -361: 24102, -360: 58578, -359: 59275, -358: 60330, -357: 61287, -356: 62499, -355: 62656, -354: 63782, -353: 63683, -352: 63309, -351: 61591, -350: 57721, -349: 48178, -348: 24879, -347: 57812, -346: 58888, -345: 60319, -344: 61017, -343: 61910, -342: 63069, -341: 63782, -340: 64199, -339: 63764, -338: 62469, -337: 58683, -336: 48274, -335: 26070, -334: 57315, -333: 58156, -332: 59062, -331: 60336, -330: 61637, -329: 62677, -328: 63640, -327: 64065, -326: 63612, -325: 62402, -324: 58887, -323: 48657, -322: 26139, -321: 56220, -320: 57372, -319: 58193, -318: 59381, -317: 60734, -316: 61660, -315: 62874, -314: 63184, -313: 63406, -312: 62191, -311: 58261, -310: 48561, -309: 26324, -308: 54653, -307: 56003, -306: 57035, -305: 58442, -304: 59545, -303: 60604, -302: 61686, -301: 62680, -300: 62290, -299: 61423, -298: 57886, -297: 48032, -296: 25673, -295: 53036, -294: 54153, -293: 55281, -292: 56236, -291: 57671, -290: 58974, -289: 59968, -288: 60704, -287: 60858, -286: 59794, -285: 56528, -284: 46753, -283: 25595, -282: 50158, -281: 51784, -280: 52674, -279: 54161, -278: 55336, -277: 56784, -276: 57621, -275: 58420, -274: 58593, -273: 57705, -272: 54233, -271: 45602, -270: 24698, -269: 46419, -268: 48024, -267: 48985, -266: 50720, -265: 51841, -264: 52949, -263: 54174, -262: 54875, -261: 55026, -260: 54280, -259: 51242, -258: 42375, -257: 23290, -256: 40553, -255: 42139, -254: 43084, -253: 44560, -252: 45986, -251: 47221, -250: 48523, -249: 49630, -248: 49847, -247: 48977, -246: 45991, -245: 38551, -244: 20920, -243: 31640, -242: 32719, -241: 34343, -240: 35660, -239: 36402, -238: 38075, -237: 39447, -236: 40556, -235: 40764, -234: 39946, -233: 37762, -232: 31543, -231: 17278, -230: 15367, -229: 16238, -228: 17281, -227: 18433, -226: 19590, -225: 20835, -224: 21881, -223: 23137, -222: 23449, -221: 23106, -220: 22368, -219: 18525, -218: 10547, -217: 13173, -216: 14056, -215: 14840, -214: 16336, -213: 17175, -212: 18679, -211: 19470, -210: 20344, -209: 20827, -208: 20648, -207: 19584, -206: 16730, -205: 9433, -204: 11085, -203: 11850, -202: 12666, -201: 13377, -200: 14372, -199: 15679, -198: 16719, -197: 17615, -196: 17973, -195: 18213, -194: 17011, -193: 14448, -192: 8162, -191: 8626, -190: 9474, -189: 10017, -188: 10990, -187: 11936, -186: 12837, -185: 13772, -184: 14621, -183: 15188, -182: 15266, -181: 14198, -180: 12159, -179: 7111, -178: 6385, -177: 6846, -176: 7523, -175: 8354, -174: 9062, -173: 9974, -172: 10758, -171: 11609, -170: 11887, -169: 12030, -168: 11593, -167: 9687, -166: 5875, -165: 4182, -164: 4568, -163: 5343, -162: 5855, -161: 6359, -160: 7027, -159: 7566, -158: 8286, -157: 8803, -156: 8900, -155: 8633, -154: 7365, -153: 4375, -152: 2404, -151: 2695, -150: 2961, -149: 3529, -148: 3747, -147: 4395, -146: 4882, -145: 5208, -144: 5626, -143: 5642, -142: 5599, -141: 4782, -140: 2979, -139: 944, -138: 1168, -137: 1270, -136: 1479, -135: 1685, -134: 2034, -133: 2283, -132: 2586, -131: 2746, -130: 2909, -129: 2771, -128: 2456, -127: 1645, -126: 174, -125: 210, -124: 242, -123: 345, -122: 435, -121: 481, -120: 544, -119: 653, -118: 727, -117: 814, -116: 830, -115: 718, -114: 504, -113: 3, -112: 7, -111: 7, -110: 11, -109: 16, -108: 18, -107: 18, -106: 29, -105: 49, -104: 46, -103: 35, -102: 44, -101: 32},
}

def num2eff(num, k=0):
    return num2npass[k][num] / float(num2nevt[num])

tau2range = defaultdict(list)

nums = []
num = -100
for tau0 in tau0s:
    print 'tau%05ium' % tau0, num-1, 'to',
    for mass in masses:
        num -= 1
        nums.append(num)
        name = make_name(tau0, mass)

        num2tau[num] = tau0
        num2mass[num] = mass
        name2num[name] = num
        num2name[num] = name
        name2mass[name] = mass

        tau2range[tau0].append(num)

        nevt = 100000

        if mass == 400:
            if tau0 in (100, 200, 300, 500, 600, 800, 10000):
                nevt -= 200
            elif tau0 == 400:
                nevt -= 600
            elif tau0 == 6000:
                nevt -= 400
        elif mass == 1000:
            if tau0 == 26000:
                nevt -= 200
        elif mass == 1500:
            if tau0 == 300:
                nevt -= 400
            elif tau0 == 16000 or tau0 == 28000:
                nevt -= 200
        elif mass == 300:
            if tau0 in (500, 700, 900, 3000, 20000, 24000):
                nevt -= 200
        elif mass == 500:
            if tau0 == 600:
                nevt -= 200
        elif mass == 700:
            if tau0 in (200, 5000, 7000, 9000, 10000, 24000):
                nevt -= 200
        elif mass == 600:
            if tau0 == 600:
                nevt -= 200
            elif tau0 == 16000:
                nevt -= 400
        elif mass == 900:
            if tau0 == 20000:
                nevt -= 200
        elif mass == 1300:
            if tau0 == 8000:
                nevt -= 200
        elif mass == 1200:
            if tau0 in (500, 600, 700, 800, 1000, 9000, 14000, 28000):
                nevt -= 200
            elif tau0 == 200:
                nevt -= 400
            elif tau0 == 6000:
                nevt -= 1000
            elif tau0 == 20000:
                nevt -= 2000
        elif mass == 800:
            if tau0 == 300 or tau0 == 8000:
                nevt -= 200
        elif mass == 1100:
            if tau0 in (100, 200, 600, 900, 5000, 16000):
                nevt -= 200
            elif tau0 in (400, 800, 2000):
                nevt -= 400

        elif tau0 == 32000:
            if mass in (600, 1400):
                nevt -= 200
            elif mass == 1300:
                nevt -= 600
        elif tau0 == 40000:
            if mass == 1500:
                nevt -= 1600
            elif mass == 1300:
                nevt -= 2800
            elif mass in (1100, 1400):
                nevt -= 2000
            elif mass in (600, 900):
                nevt -= 200
            elif mass == 1000:
                nevt -= 400
            elif mass == 1200:
                nevt -= 1000
            elif mass == 800:
                nevt -= 600
        elif tau0 == 42000:
            if mass in (700, 800, 900, 1000):
                nevt -= 200
            elif mass in (1100, 1200):
                nevt -= 600
            elif mass == 1400:
                nevt -= 1000
            elif mass == 1500:
                nevt -= 400
            elif mass == 1300:
                nevt -= 2800
        elif tau0 == 38000:
            if mass in (500, 1000, 1100, 1200):
                nevt -= 200
            elif mass == 1300:
                nevt -= 600
            elif mass == 1500:
                nevt -= 1200
            elif mass == 1400:
                nevt -= 1000
        elif tau0 == 36000:
            if mass == 600:
                nevt -= 200
            elif mass in (1000, 1200, 1400):
                nevt -= 400
            elif mass == 1300:
                nevt -= 600
            elif mass == 1500:
                nevt -= 800
        elif tau0 == 34000:
            if mass in (700, 1400):
                nevt -= 400
            elif mass in (800, 1000, 1200):
                nevt -= 200
            elif mass == 1300:
                nevt -= 800

        num2nevt[num] = nevt

        path = 'root://cmsxrootd.fnal.gov//store/user/tucker/mfv_sample_scan/'
        if mass in [300, 500, 700, 900, 1300] and tau0 < 32000:
            path = path.replace('tucker', 'jchu')
        fn = path + name + '.root'
        name2fn[name] = fn
    print num

tau2range = dict(tau2range)

print 'last num =', num

def make_templates(out_fn, in_fn):
    from JMTucker.MFVNeutralino.MiniTreeBase import ROOT, make_h

    num2npass = {}
    num2npass600 = {}
    num2npass800 = {}

    fin = ROOT.TFile(in_fn)
    f = ROOT.TFile(out_fn, 'recreate')
    hs = []

    for num in reversed(num2name.keys()):
        hname = 'sig%i' % num
        name = num2name[num]
        hin = fin.Get(hname)
        if hin:
            print 'copy %i -> %s from %s:%s' % (num, name, in_fn, hname)
            h = hin.Clone()
        else:
            fn = name2fn[name]
            print fn
            h = make_h(fn, 'sig%i' % num)

        hs.append(h)
        h.SetDirectory(f)

        num2npass[num] = int(h.GetEntries())
        num2npass600[num] = int(h.Integral(h.FindBin(0.061), 1000))
        num2npass800[num] = int(h.Integral(h.FindBin(0.081), 1000))

    f.Write()
    f.Close()

    print
    print 'new_num2npass = {'
    print '    0: %r,' % num2npass
    print '    600: %r,' % num2npass600
    print '    800: %r,' % num2npass800
    print '}'

def book(name, title):
    import ROOT
    h = ROOT.TH2F(name, title + ';neutralino mass (GeV);neutralino lifetime (#mum)', nmasses, array('d', masses + [1600]), ntau0s, array('d', tau0s + [44000]))
    h.SetStats(0)
    return h

def all_points():
    for num in nums:
        tau0 = num2tau[num]
        mass = num2mass[num]
        yield (num, tau0, mass)

def make_h_eff(k):
    h = book('h_eff' + ('_%i' % k if k != 0 else ''), '')
    for num, tau0, mass in all_points():
        h.SetBinContent(h.FindBin(mass, tau0), num2eff(num, k))
    return h

def draw_h_effs():
    from JMTucker.Tools.ROOTTools import *
    set_style()
    rainbow_palette()
    c = ROOT.TCanvas('c', '', 800, 800)
    for k in (0, 600, 800):
        h = make_h_eff(k)
        h.Draw('colz')
        c.SaveAs('/uscms/home/tucker/asdf/a_%i.png' % k)
        
def stat_errors():
    from JMTucker.Tools.ROOTTools import ROOT
    f = ROOT.TFile('bigsigscan.root')
    mx = 0
    for num, tau0, mass in all_points():
        if tau0 < 300:
            continue
        h = f.Get('sig%i' % num)
        nbins = h.GetNbinsX()
        m = max(h.GetBinError(i) / h.GetBinContent(i) for i in xrange(1, nbins+1))
        mx = max(m, mx)
        print tau0, mass, m, mx

def extract_nevt():
    from JMTucker.Tools.ROOTTools import ROOT
    f = ROOT.TFile('h_minitree_entries.root')
    h = f.Get('h_minitree_entries')

    l = defaultdict(lambda : defaultdict(list))
    for ibin in xrange(1,h.GetNbinsX()+1):
        nm = h.GetXaxis().GetBinLabel(ibin)
        nj = h.GetBinContent(ibin)
        miss = 200*(500 - int(float(nj)))
        if miss:
            t,m = nm[1:].split('M')
            t = int(t)*100
            m = int(m)*100
            l[t][miss].append(m)

    for t in l:
        print 'elif tau0 == %i:' % t
        for i, (miss, masses) in enumerate(l[t].iteritems()):
            elly = 'el' if i > 0 else ''
            if len(masses) > 1:
                print '    %sif mass in %r:' % (elly, tuple(masses))
                print '        nevt -= %i' % miss
            else:
                print '    %sif mass == %r:' % (elly, masses[0])
                print '        nevt -= %i' % miss

def test_new_num2npass():
    problem = False
    for a in (0, 600, 800):
        zk = set(new_num2npass[a].keys())
        nk = set(num2npass[a].keys())
        com = zk & nk
        print a, ': in common:', len(com)
        for c in com:
            if new_num2npass[a][c] != num2npass[a][c]:
                print 'problem: with', c, ': new', new_num2npass[a][c], ' old:', num2npass[a][c]
                problem = True
    if problem:
        print '  YIKES!'

if __name__ == '__main__':
    if 'make' in sys.argv:
        make_templates('bigsigscan.root', 'bigsigscan.last.root')
