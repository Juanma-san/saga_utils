import sys
import PyPDF2
import re
from pathlib import Path

pdf_file = None
pdf_reader = None
num_alumnes = 0
CAR_INICIAL = 203
CAR_FINAL = 270
CARPETA_NOTES = "./notes_separades"

def open_pdf_reader(nom):
	try:
		pdf_file = open(nom, 'rb')
		pdf_reader = PyPDF2.PdfFileReader(nom)
		return pdf_reader
		
	except FileNotFoundError:
		raise FileNotFoundError(f"No s'ha trobat el pdf '{nom}'.");

# Alliberar recursos	
def close_src_pdf():
	try:
		pdf_reader.close()
		pdf_file.close()
	except:
		pass


#Mètode principal
def trenca_notes_en_alumnes(fitxer):
	reader = open_pdf_reader(fitxer)
	pdf_writer = PyPDF2.PdfFileWriter()
	
	alumne_anterior = None
	al = None
	
	Path(CARPETA_NOTES).mkdir(parents=True, exist_ok=True)
	
	# Iterar les pàgines del pdf
	for page_num in range(len(reader.pages)):
		page = reader.pages[page_num]
		
		al = find_alumne_en_pagina(page)
		if al == None: #pàgina en blanc
			#print(f"DEBUG: pàgina-{page_num+1} en blanc")
			continue

		#print(f"DEBUG: pag-{page_num}: {al}")
		
		#Inicialment són iguals
		if alumne_anterior == None:
			alumne_anterior = al
			
		#print("DEBUG: ",al)
	
		if al == alumne_anterior:
			pdf_writer.addPage(page) #Afegim al buffer la pàgina

		# Si canviem d'alumne escrivim el que tenim		
		else:
			nom_pdf_alumne = get_nom_pdf(alumne_anterior)
			print(f"DEBUG: guardant - {alumne_anterior[-1]} - pdf='{nom_pdf_alumne}'")
			
			save_buffer_to_pdf(nom_pdf_alumne, pdf_writer)
			
			pdf_writer = PyPDF2.PdfFileWriter() #Reset del buffer
			
			#num_alumnes += 1
			
			pdf_writer.addPage(page) #pàgina actual al buffer nou
			#Fins al proper
			alumne_anterior = al
	
	#Hem de guardar el darrer
	if al != None:
		#print(f"DEBUG: final al={al}")
		nom_pdf_alumne = get_nom_pdf(al)
	else:
		nom_pdf_alumne = get_nom_pdf(alumne_anterior)
		#print(f"DEBUG: final alumne_anterior={alumne_anterior}")
	
	print(f"DEBUG: guardant - {alumne_anterior[-1]} - pdf='{nom_pdf_alumne}'")
	
	save_buffer_to_pdf(nom_pdf_alumne, pdf_writer)
	'''
	pdf_sortida = open(nom_pdf_alumne, 'wb')
			
	pdf_writer.write(pdf_sortida)
	pdf_sortida.close()

	#num_alumnes +=1
	'''	
	close_src_pdf()
	print(f"Num butlletins totals = {num_alumnes}")


def save_buffer_to_pdf(nom_pdf, writer):
	global num_alumnes
	
	pdf_sortida = open(nom_pdf, 'wb')
	writer.write(pdf_sortida)
	pdf_sortida.close()
	
	num_alumnes += 1
			
def get_nom_pdf(alumne):
	nom_pdf_alumne = alumne[0]
	nom_pdf_alumne = f"{CARPETA_NOTES}/{nom_pdf_alumne}.pdf"
	
	return nom_pdf_alumne


def find_alumne_en_pagina(pag):
	#print("buscant alumne")
	page_text = pag.extractText()
	
	if page_text == "":
		return None
		
	#print(f"DEBUG: extracte->'{page_text[CAR_INICIAL-10:CAR_FINAL]}'")
	#Tallem la cadena de l'alumne entre els textos anteriors i posteriors
	txt_nom = re.search(r'Alumne(DNI|NIE|Passaport)Grup(.*?)CFPS', page_text).group(2)
	#print(f"DEBUG: {txt_nom}")

	#Tallem el NIF
	nif = txt_nom[-9:]
	txt_nom = txt_nom[0:-9]
	
	return [txt_nom, nif]


if __name__ == '__main__':
    if len(sys.argv) > 1:
    	pdf_file = sys.argv[1]
    else:
    	print("WARN: No pdf param -> nom per defecte 'notes.pdf'")
    	pdf_file = "notes.pdf"
    
    trenca_notes_en_alumnes(pdf_file)
