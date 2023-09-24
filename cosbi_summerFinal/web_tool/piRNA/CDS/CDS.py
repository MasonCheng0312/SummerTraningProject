import csv
with open('CDS.csv','r',encoding='utf8') as f1:
	reader1 = csv.reader(f1)
	CDS={}
	key=''
	key_check=[]
	value=''
	for i in reader1:
		if i[0]!='':
			value=i[0].replace(u'\ufeff', '')
			CDS[i[1].replace('*','')]=value
		else:
			CDS[i[1].replace('*','')]=value
with open('RNAgene.txt','r') as f2:
	a=1
	CDS_1 = CDS_2 = 0
	for x in f2:
		if a==1:
			RNA = x.strip()
			a+=1
		elif a==2:
			a+=1
			continue
		elif a==3:
			CDS_1 = int(x.strip())
			a+=1
		elif a==4:
			CDS_2 = int(x.strip())
CDS_str = ''
start=CDS_1
while start < CDS_2:
	CDS_str+=CDS[RNA[start-1:start+2]].upper()
	start+=3
print(CDS_str)			