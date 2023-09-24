import argparse
import sys
import ast
import re
import csv
from multiprocessing import Process, Lock, Queue ,JoinableQueue, active_children
import json
import math
import operator

def strtr(text, dic):
	# Create a regular expression  from the dictionary keys
	import re
	regex = re.compile("(%s)" % "|".join(map(re.escape, dic.keys())))
	# For each match, look-up corresponding value in dictionary
	return regex.sub(lambda mo: str(dic[mo.string[mo.start():mo.end()]]), text)

def complement(seq):
	replacements = {
	"A" : "U",
	"U" : "A",
	"G" : 'C',
	"C" : 'G'
	}
	out = strtr(seq,replacements)
	return out

def scan(q,num,Arr2,options):
	global piRNA_Length
	# 讀取piRNA序列
	with open('piRNA/{0}/piRNA{1}.txt'.format(options['nematodeType'],num+1),'r') as f1:
		reader1 = csv.reader(f1)
		ArrPiRNA = []
		piRNA_information = []
		for x in reader1:
			ArrPiRNA.append([x[0],x[1].strip()])
			piRNA_Length = len(x[1])
			x.pop(0)
			x.pop(0)
			ArrPiRNA[len(ArrPiRNA)-1].append(x)

	#開始逐個site進行掃描比對
	outArr = []
	for key in ArrPiRNA:
		print(key)
		Arr1 = list(complement(key[1][::-1]))   #piRNA做reverse compliment然後將字符切成21個陣列
		for a in range(len(Arr2)-len(Arr1)+1): # a=輸入序列掃描次序 a次數不會大於(總長-piRNA長)，用range所以+1
			GG = 1 
			Arr4 = []	#Arr4存沒對到的位置
			ArryxGU = []  #ArryxGU存non-GU的錯誤位置
			Arr3 = list(key[1][::-1])
			Arr5 = list(key[1][::-1])  #Arr5存piRNA的Reverse秀結果用 



			"""每個site從piRNA位置2開始往左確認每一個位置是否對到 
				d計算#seed_non_GU m計算#seed_GU e計算#non_seed_non_GU  n計算#non_seed_GU 
				o儲存piRNA位置1的配對情形"""

			b = a +len(Arr1)-2
			c = len(Arr1)-2
			d = 0
			e = 0
			m = 0
			n = 0
			o = 0
			while(b>=a):				
				if c >= len(Arr1)-7 and Arr2[b] != Arr1[c]:
					# seed區沒對到
					if (Arr2[b]=='G' and Arr1[c]=='A') or (Arr2[b]=='U' and Arr1[c]=='C'):
						#沒對到的是GU    
						if m == int(options['core_GU']):
							b-=1
							c-=1
							break
						Arr3[c] = Arr2[b]
						Arr5[c] = "<mark id='b'>"+Arr5[c]+"</mark>"
						Arr4.append("<mark id='b'>"+str(len(Arr1)-c)+"</mark>")
						m+=1
					else:
						#沒對到的不是GU
						if d == int(options['core_non_GU']):
							b-=1
							c-=1
							break
						Arr3[c] = Arr2[b]
						Arr5[c] = "<mark>"+Arr5[c]+"</mark>"
						ArryxGU.append(str(len(Arr1)-c))
						Arr4.append("<mark>"+str(len(Arr1)-c)+"</mark>")
						d+=1
					b-=1
					c-=1


				elif Arr2[b] == Arr1[c] and b != a :
					# 對到的情況
					Arr3[c] = Arr2[b]
					b-=1
					c-=1

				elif d + e + m + n > int(options['total']) or (options['pts'][0] == 'true' and 10-d*scoreA-m*scoreB-e*scoreC-n*scoreD < options['pts'][1]):
					#錯誤總數大於total
					b-=1
					c-=1
					break


				elif c<len(Arr1)-7 and Arr2[b] != Arr1[c] and b != a:
					# non_seed區沒對到的情況
					if (Arr2[b]=='G' and Arr1[c]=='A') or (Arr2[b]=='U' and Arr1[c]=='C'):
						#沒對到的是GU    
						if n == int(options['non_core_GU']):
							b-=1
							c-=1
							break
						Arr3[c] = Arr2[b]
						Arr5[c] = "<mark id='b'>"+Arr5[c]+"</mark>"
						Arr4.append("<mark id='b'>"+str(len(Arr1)-c)+"</mark>")
						n+=1
					else:
						#沒對到的不是GU
						if e == int(options['non_core_non_GU']):
							b-=1
							c-=1
							break
						Arr3[c] = Arr2[b]
						Arr5[c] = "<mark>"+Arr5[c]+"</mark>"
						ArryxGU.append(str(len(Arr1)-c))
						Arr4.append("<mark>"+str(len(Arr1)-c)+"</mark>")
						e+=1
					b-=1
					c-=1


				elif b == a:
					# 掃到該site最左邊位置的情況

					if Arr2[b] != Arr1[c]:
						if (Arr2[b]=='G' and Arr1[c]=='A') or (Arr2[b]=='U' and Arr1[c]=='C'):
							#沒對到的是GU    
							if n == int(options['non_core_GU']):
								b-=1
								c-=1
								break
							Arr3[c] = Arr2[b]
							Arr5[c] = "<mark id='b'>"+Arr5[c]+"</mark>"
							Arr4.append("<mark id='b'>"+str(len(Arr1)-c)+"</mark>")
							n+=1
						else:
							#沒對到的不是GU
							if e == int(options['non_core_non_GU']):
								b-=1
								c-=1
								break
							Arr3[c] = Arr2[b]
							Arr5[c] = "<mark>"+Arr5[c]+"</mark>"
							ArryxGU.append(str(len(Arr1)-c))
							Arr4.append("<mark>"+str(len(Arr1)-c)+"</mark>")
							e+=1
					elif Arr2[b] == Arr1[c] :
						Arr3[c] = Arr2[b]
					Arr3[len(Arr1)-1] = Arr2[a+len(Arr1)-1]
					if Arr2[a+len(Arr1)-1] != Arr1[len(Arr1)-1] :
						if (Arr2[a+len(Arr1)-1]=='G' and Arr1[len(Arr1)-1]=='A') or (Arr2[a+len(Arr1)-1]=='U' and Arr1[len(Arr1)-1]=='C'):
							#沒對到的是GU    
							Arr5[len(Arr1)-1] = "<mark id='g'>"+Arr5[len(Arr1)-1]+"</mark>"
							Arr4.insert(0,"<mark id='g'>1</mark>")
						else:
							#沒對到的不是GU
							Arr5[len(Arr1)-1] = "<mark id='g'>"+Arr5[len(Arr1)-1]+"</mark>"
							Arr4.insert(0,"<mark id='g'>1</mark>")
							ArryxGU.insert(0,'1')
						o+=1
					if d + e + m + n > int(options['total']) or (options['pts'][0] == 'true' and 10-d*scoreA-m*scoreB-e*scoreC-n*scoreD < options['pts'][1]):
						b-=1
						c-=1
						break
					Arr3[len(Arr1)-2] = Arr3[len(Arr1)-2]+"<span id='L'>|</span>"
					Arr5[len(Arr1)-2] = Arr5[len(Arr1)-2]+"<span id='L'>|</span>"
					Arr3[len(Arr1)-8] = Arr3[len(Arr1)-8]+"<span id='L'>|</span>"
					Arr5[len(Arr1)-8] = Arr5[len(Arr1)-8]+"<span id='L'>|</span>"
					if Arr4 == [] :
						Arr4 = 'N/A'
					if ArryxGU == [] :
						ArryxGU = 'N/A'
								
					outArr.append([key[0],str(a+1)+'-'+str(a+21),o+d+e+m+n,','.join(Arr4),','.join(ArryxGU),d,m,e,n,"<span style=\"white-space:nowrap\">5' "+''.join(Arr3)+" 3'","3' "+''.join(Arr5)+" 5'</span>",key[2],key[1][::-1],str(a+1).zfill(5),10-d*scoreA-m*scoreB-e*scoreC-n*scoreD])
					GG+=1
					b-=1
					c-=1
	if outArr==[]:
		outArr = 'N/A'
	q.put(outArr)

parser = argparse.ArgumentParser()
with open(sys.argv[1],'r') as inSeq:
	inputSeqName = inSeq.readline().strip().replace('>','').replace('\n','')
	inputSeq = inSeq.readline().strip().upper().replace('T','U')

nematodeType = sys.argv[2]
if nematodeType == 'cb':
	nematodeType = 'C.briggsae'
elif nematodeType == 'ce':
	nematodeType = 'C.elegans'
else:
	sys.exit('nematode Type error!')

CDS = sys.argv[3]
if CDS == 'whole':
	CDS_A = '-555'
	CDS_B = '-555'
elif CDS == 'none':
	CDS_A = 0
	CDS_B = 0
else:
	CCC = CDS.split('-')
	CDS_A = int(CCC[0])
	CDS_B = int(CCC[1])

rulesList = ast.literal_eval(sys.argv[4])
if len(rulesList) == 6:
	pts_switch = 'true'
	ptsss = rulesList[5]
else:
	pts_switch = 'false'
	ptsss = 0

global scoreA,scoreB,scoreC,scoreD
scoreA = 7
scoreB = 1.5
scoreC = 2
scoreD = 1.5


# 各種防呆
if inputSeq == '':
	print('noSeq')
	sys.exit('nematode Type error!')
else:
	if inputSeqName == '':
		sys.exit('noSeqName')

	name = inputSeqName
	RNA = inputSeq
	if re.search("^[AUCG]+$",RNA) == None:
		sys.exit('input Seq is weird')


	Arr2 = list(RNA)
	options = {'core_non_GU':rulesList[0],'core_GU':rulesList[1],'non_core_non_GU':rulesList[2],'non_core_GU':rulesList[3],'total':rulesList[4],'nematodeType':nematodeType,'pts':[pts_switch,ptsss]}
	with open('piRNA/{0}/info_name.csv'.format(options['nematodeType']),'r') as f2:
		reader2 = csv.reader(f2)
		info_names = []
		for x in reader2:
			info_names.append(x[0])

	############ CDS防呆
	if CDS_A == '-555':
		CDS1 = 1		
	elif CDS_A is '0' : 
		sys.exit('CDS error')
	elif CDS_A!='' :
		if float(CDS_A)%1 !=0 : 
			sys.exit('CDS error')
		else:
			CDS1 = int(CDS_A)				
	else: 
		CDS1 = 0

	if CDS_B == '-555':
		CDS2 = len(Arr2)
		CDS_region = 'Whole input sequence (1 - '+str(CDS2)+')'		
	elif CDS_B is '0' : 		
		sys.exit('CDS error')
	elif CDS_B!='' :
		if float(CDS_B)%1 !=0 :		
			sys.exit('CDS error')
		else:
			CDS2 = int(CDS_B)
			CDS_region = str(CDS1)+' - '+str(CDS2)
	else:
		CDS2 = 0
		CDS_region = 'None'

	if (CDS1==0 and CDS2!=0) or (CDS2==0 and CDS1!=0) or ((CDS1!= 0 and CDS2!= 0) and ((CDS1 >= CDS2) or ((CDS2-CDS1-2)%3 !=0) or (CDS2 > len(Arr2)) or (CDS1 < 1))):
		sys.exit('CDS error')
	#################################################################

	# 通過防呆才會進入下方主程序
	else:
		#各物種多工進程任務數量
		mission_count = {'C.elegans':357, 'C.briggsae':290, 'C.brenneri':1157, 'C.remanei':813}
		result=[]

		# 下多工命令
		q = JoinableQueue()
		for num in range(mission_count[options['nematodeType']]):
			Process(target=scan, args=(q, num ,Arr2 ,options)).start()

		# 各多工任務結果蒐集
		for t in range(mission_count[options['nematodeType']]):
			a = q.get()
			if a != 'N/A':
				for x in a:
					result.append(x)
			q.task_done()
		q.join()
		outForAdvice = result

		data = {
			'gene':RNA,
			'name':name,
			'newout':result,
			'options':options,
			'CDS1':CDS1,
			'CDS2':CDS2,
			'CDS_region':CDS_region,
			'Tscore':[scoreA,scoreB,scoreC,scoreD],
		}

		with open('output/piRNA_targeting_sites.json','w') as w1:
			json.dump(data,w1,indent=4)

		result = sorted(result, key = lambda l:(l[14],-int(l[1].split('-')[0])),reverse=True)

		with open('output/piRNA_targeting_sites.csv','w') as w1:
			wr1 = csv.writer(w1)
			wr1.writerow(['Sequence name: '+ name])
			wr1.writerow(['Specify coding sequence (CDS) region: '+ CDS_region])
			wr1.writerow(['piRNA targeting rules: '])
			wr1.writerow(['Seed region: non-GU: up to {0}, GU: up to {1}'.format(options['core_non_GU'],options['core_GU'])])
			wr1.writerow(['Non-seed region: nonGU: up to {0}, GU: up to {1}'.format(options['non_core_non_GU'],options['non_core_GU'])])
			wr1.writerow(['Total mismatches: up to {0}'.format(options['total'])])
			if options['pts'][0] == 'true':
				wr1.writerow(['piRNA targeting score: more than or equal to {0}'.format(options['pts'][1])])
			wr1.writerow([''])
			wr1.writerow(['piRNA','piRNA targeting score','targeted region in input sequence','# mismatches','position in piRNA','# non-GU mismatches in seed region','# GU mismatches in seed region','# non-GU mismatches in non-seed region','# GU mismatches in non-seed region','5\' Input sequence 3\'','3\' piRNA 5\''])
			for td in result:				
				piName = td[0]
				detailTopStr = re.sub("<.*?>", "", td[9]).replace("5' ",'').replace(" 3'",'').replace("|",'')
				detailBotStr = re.sub("<.*?>", "", td[10]).replace("3' ",'').replace(" 5'",'').replace("|",'')
				detail = detailTopStr + '\n' + detailBotStr
				wr1.writerow([piName,10-int(td[5])*scoreA-int(td[6])*scoreB-int(td[7])*scoreC-int(td[8])*scoreD,td[1],td[2],re.sub("<.*?>", "", td[3]),td[5],td[6],td[7],td[8],detailTopStr,detailBotStr])
