from ImpararePackage import dataRequest
from multiprocessing import Pool, cpu_count
from ImpararePackage import maestro
import pandas as pd

def worker(c = pd.DataFrame):
    
    c = maestro.copy_columns(df= c, column= "atb")
    
    translate_atb = {
        #ACICLOVIR
        "ACICLOVIR 200MG COMP - ZOVIRAX" : "INTERMEDIARIO",
        "ACICLOVIR 400 MG COMP" : "INTERMEDIARIO",
        "ACICLOVIR 400MG COMP" : "INTERMEDIARIO",
        "ACICLOVIR (50MG/G) TB 10G CREME TOPICO - ZOVIRAX" : "INTERMEDIARIO",
        "ACICLOVIR FA 250MG PO LIOFILIZADO INJ - UNI VIR" : "INTERMEDIARIO",
        "ACICLOVIR FA 250MG PO LIOF INJ - UNI VIR" : "INTERMEDIARIO",
        "ACICLOVIR 250MG IV INJ." : "INTERMEDIARIO",
        "ACICLOVIR 200MG CP." : "INTERMEDIARIO",
        #AMICACINA
        "AMICACINA - 100MG (50MG/ML) AMP 2ML INJ - AMICACINA" : "HOSPITALAR",
        "AMICACINA 500MG (250MG/ML) AMP 2ML INJ - AMICACINA" : "HOSPITALAR",
        "AMICACINA 500MG INJ. AMPOLA C/ 2ML" : "HOSPITALAR",
        "AMICACINA 100MG INJ. AMPOLA C/ 2ML" : "HOSPITALAR",
        #AMOX+CLAV
        "AMOXICIL+CLAVULAN (400MG+57MG/5ML) FR 70ML OR - CLAVULIN BD" : "OUTROS",
        "AMOXICILINA+CLAVULANAT (250MG+62,5MG/5ML) FR 75ML - CLAVULIN" : "OUTROS",
        "AMOXICILINA+CLAVULANATO 1G/200MG FA INJ - DOCLAXIN" : "OUTROS",
        "AMOXICILINA 500MG + CLAVULANATO 125MG COMP - CLAVULIN" : "OUTROS",
        "AMOXICILINA 500MG+ACIDO CLAVULANICO 125MG COMP - CLAVULIN BD" : "OUTROS",
        "AMOXICILINA 500MG + CLAV. DE POTÁSSIO 125MG CP." : "OUTROS",
        "AMOXICILINA + CLAV. DE POTASSIO (1000MG+200MG)" : "OUTROS",
        "AMOXICILINA+CLAVULANATO DE POTÁSSIO (400MG + 57MG/5ML) - 70 ML" : "OUTROS",
        #AMOXICILINA
        "AMOXICILINA (250MG/5ML) FR 150ML PO SUS OR - AMOXIL" : "OUTROS",
        "AMOXICILINA 500MG CAPS - AMOXIL" : "OUTROS",
        "AMOXICILINA 500MG CAPS." : "OUTROS",
        "AMOXICILINA 400MG/5ML SUSP. C/ 100ML" : "OUTROS",
        #AMOXICILINA_SULBACTAM            
        "AMOXICILIN+SULBACT (200MG+50MG/ML) PO SUS FR 30ML - TRIFAMOX" : "OUTROS",
        "AMOXI+SULBAC IBL BD 250MG/ML FR 30ML SUP - TRIFAMOX" : "OUTROS",
        #AMPICILINA
        "AMPICILINA FA 1G PO INJ" : "INTERMEDIARIO",
        "AMPICILINA 1,0G E SULBACTAM 0,5G INJETÁVEL" : "INTERMEDIARIO",
        "AMPICILINA 1G  INJ." : "INTERMEDIARIO",
        #AMPICILINA_SULBACTAM
        "SULBACTAM 1,0G + AMPICILINA 2,0G PO INJ FA 3G" : "OUTROS",
        "SULBACTAM+AMPICILINA (0,5G+1,0G) FA 1,5G PO SOL INJ - UNASYN" : "OUTROS",
        "AMPICILINA 2,0G + SULBACTAM 1,0G INJETÁVEL" : "OUTROS",
        #ANFOTERICINA
        "ANFOTERICINA B 50MG INJ. 10ML" : "ANTIFUNGICO",
        #AZITROMICINA
        "AZITROMICINA 500MG COMP - ZITROMAX" : "OUTROS",
        "AZITROMICINA 600MG (200MG/5ML) FR 15ML PO SUSP ORAL - ASTRO" : "OUTROS",
        "AZITROMICINA 600MG (40MG/ML) FR 15ML PO SUSP OR - ASTRO" : "OUTROS",
        "AZITROMICINA FA 500MG PO LIOF SOL INJ - ZITROMAX" : "OUTROS",
        "INATIVO AZITROMICINA 600MG (200MG/5ML) FR 15ML PO SU - ASTRO" : "OUTROS",
        "AZITROMICINA 200MG/5ML SUSP. ORAL 15ML" : "OUTROS",
        "AZITROMICINA 500MG CP." : "OUTROS",
        #AZTREONAM
        "AZTREONAM 1G" : "MMR",
        #PENICILINAGBENZATINA
        "BENZILPENICILINA 1.200.000 (300.000U/ML) FA 4ML - BENZETACIL" : "COMUNITARIO",
        "BENZILPENICILINA (300.000U/ML) FA 4ML SUSP INJ - BENZETACIL" : "COMUNITARIO",
        "BENZILPENICILINA FA 400.000 UI PO INJ - PENKARON" : "COMUNITARIO",
        "BENZILPENICILINA POTÁSSICA 5.000.000UI INJ. (A)" : "COMUNITARIO",
        "BENZILPENICILINA 1.200.000UI INJ. - 4ML" : "COMUNITARIO",
        #PENICILINAGPOTASSICA
        "PENICILINA  5.000.000UI INJ - ARICILINA" : "COMUNITARIO",
        "PENICILINA FA 5.000.000 UI PO INJ - ARICILINA" : "COMUNITARIO",
        "PENICILINA G POTÁSSICA 5.000.000UI INJ. (A)" : "COMUNITARIO",
        #CEFADROXILA
        "CEFADROXILA (250MG/5ML) FR P/100ML PO SUSP ORAL" : "OUTROS",
        "CEFADROXILA 500MG CAPS - CEFAMOX" : "OUTROS",
        "CEFADROXILA 500MG CP." : "OUTROS",
        "CEFADROXILA (50MG/ML) FR 100ML PO SUSP ORAL" : "OUTROS",
        "CEFADROXILA SUSPENSÃO 250MG/5ML" : "OUTROS",
        #CEFALEXINA
        "CEFALEXINA 250MG/5ML (50MG/ML) FR 100ML SUSP ORAL - KEFLEX" : "COMUNITARIO",
        "CEFALEXINA 500MG COMP - KEFLEX " : "COMUNITARIO",
        "KEFLEX 250MG/5ML (50MG/ML) FR100ML SUSP ORAL - CEFALEXINA" : "COMUNITARIO",
        "CEFALEXINA MONOIDRATADA 500MG DRG." : "COMUNITARIO",
        #CEFALOTINA
        "CEFALOTINA FA 1G PO SOL INJ - KEFLIN" : "OUTROS",
        "CEFALOTINA 1G" : "OUTROS",
        "CEFALOTINA 1G INJ. (A)" : "OUTROS",
        "KEFLIN FA 1G - CEFALOTINA" : "OUTROS",
        #CEFAZOLINA
        "CEFAZOLINA FA 1G (1000MG) PO SOL INJ - KEFAZOL" : "PROFILATICO",
        "CEFAZOLINA SODICA 1G FR 1000MG (R) - KEFAZOL" : "PROFILATICO",
        "CEFAZOLINA 1G INJ.  (A)" : "PROFILATICO",
        #CEFOTAXIMA
        "CEFOTAXIMA SODICA 1G INJ - CLAFORDIL" : "COMUNITARIO",
        #CEFOXITINA
        "CEFOXITINA SÓDICA 1G INJ. (A)" : "INTERMEDIARIO",
        #CEFTAZIDIMA
        "CEFTAZIDIMA 1G FA PO INJ - CEFTAZIDON" : "HOSPITALAR",
        "CEFTAZIDIMA FA 1G (1000MG) PO INJ - CEFTAZIDON" : "HOSPITALAR",
        "CEFTAZIDIMA 1G INJ." : "HOSPITALAR",
        #CEFTAZIDIMA_AVIBACTAM
        "CEFTAZIDIMA 2000MG+AVIBACTAM 500MG FA 2.5G PO - TORGENA" : "MMR",
        "CEFTAZIDIMA + AVIBACTAM 2,5G" : "MMR",
        #CEFTALOZANA_TAZOBACTAM
        "CEFTOLOZANA 1G + TAZOBACTAM 0,5G - ZERBAXA TM" : "MMR",
        #CEFTRIAXONA
        "CEFTRIAXONA 1G FA 1000MG PO INJ IV (R) - ROCEFIN" : "OUTROS",
        "CEFTRIAXONA FA 1G PO SOL INJ IM - ROCEFIN" : "OUTROS",
        "CEFTRIAXONA FA 1G PO SOL INJ IV - ROCEFIN" : "OUTROS",
        "CEFTRIAXONA - 1G IM" : "OUTROS",
        "CEFTRIAXONA FA 500MG PO SOL INJ IM - ROCEFIN" : "OUTROS",
        "CEFTRIAXONA 1G IV INJ." : "OUTROS",
        #CEFUROXIMA
        "CEFUROXIMA FA 750MG PO INJ - ZINACEF" : "OUTROS",
        "CEFUROXIMA SÓDICA 750MG INJ." : "OUTROS",
        "CEFUROXIMA  500MG CP (A)" : "OUTROS",
        #CETOCONAZOL
        "CETOCONAZOL (20MG/G) TB 30G CREME - NIZORAL" : "TOPICO",
        #CIPROFLOXACINO
        "CIPROFLOXACINO 200MG (2MG/ML) BOLS 100ML INJ - FRESOFLOX" : "OUTROS",
        "CIPROFLOXACINO 200MG (2MG/ML) BS 100ML INJ - FRESOFLOX" : "OUTROS",
        "CIPROFLOXACINO 200MG (2MG/ML) BS 100ML INJ - HIFLOXAN" : "OUTROS",
        "CIPROFLOXACINO (3,5MG/ML) FR 5ML SOL OFT - CILOXAN" : "OUTROS",
        "CIPROFLOXACINO 400MG (2MG/ML) BOLS 200ML SOL INJ IV - CIPRO" : "OUTROS",
        "CIPROFLOXACINO 400MG (2MG/ML) FR 200ML SOL INJ IV - CIPRO" : "OUTROS",
        "CIPROFLOXACINO 500MG COMP REV - CIPRO" : "OUTROS",
        "CIPROFLOXACINO 2MG/ML - 200ML" : "OUTROS",
        "CIPROFLOXACINO 500MG CP." : "OUTROS",
        #CLARITROMICINA
        "CLARITROMICINA  500MG COMP - KLARICID" : "OUTROS",
        "CLARITROMICINA 500MG FA PO LIOF INJ - CLARILIB" : "OUTROS",
        "CLARITROMICINA 500MG IV INJ." : "OUTROS",
        "CLARITROMICINA 250MG/5ML SUSPENSÃO 60ML" : "OUTROS",
        #CLINDAMICINA
        "CLINDAMICINA 300MG CAPS DURA - DALACIN" : "OUTROS",
        "CLINDAMICINA 600MG (150MG/ML) AMP 4ML INJ - HYCLIN" : "OUTROS",
        "FOSFATO DE CLINDAMICINA 600MG INJ.- 4ML (A)" : "OUTROS",
        #CEFEPIMA
        "CLORIDRATO CEFEPIMA FA 1G INJ - CLOCEF" : "HOSPITALAR",
        "CEFEPIME 1G INJ." : "HOSPITALAR", 
        #DAPTOMICINA
        "DAPTOMICINA 500MG FRASCO-AMPOLA. (A)" : "COMUNITARIO",
        #DOXICICLINA
        "DOXICICLINA 100MG COMP REV - VIBRAMICINA " : "OUTROS",
        "VIBRAMICINA 100MG COMP REV - DOXICICLINA" : "OUTROS",
        "DOXICICLINA MONOIDRATADA 100MG DRG." : "OUTROS",
        #ERTAPENEM
        "ERTAPENEM FA 1G PO LIOF INJ - INVANZ" : "OUTROS",
        #FLUCONAZOL
        "FLUCONAZOL 150MG CAPS DURA - ZOLTEC" : "ANTIFUNGICO",
        "FLUCONAZOL 200MG (2MG/ML) BOLSA 100ML SOL INF - ZOLTEC" : "ANTIFUNGICO",
        "FLUCONAZOL 2MG/ML INJ. C/ 100ML" : "ANTIFUNGICO",
        "FLUCONAZOL 150MG CÁPS." : "ANTIFUNGICO",
        #FOSFOMICINA
        "FOSFOMICINA 8G ENVELOPE(EQUIVALENTE 3G FOSFOMICINA)" : "COMUNITARIO",
        #GANCICLOVIR
        "GANCICLOVIR (1MG/ML) BOLS 500ML SOL IN PRONTO P/USO- CYMEVIR" : "OUTROS",
        "GANCICLOVIR 500MG PO FA LIOFILIZADO INJ - GANCICLOTRAT" : "OUTROS",
        "GANCICLOVIR 500MG SOL INJ BOLSA PRONTO P/ USO - CYMEVIR" : "OUTROS",
        "GANCICLOVIR FA 500MG PO LIOF INJ - GANCICLOTRAT" : "OUTROS",
        "GANCICLOVIR 500MG INJ. 10ML" : "OUTROS",
        #GENTAMICINA
        "GENTAMICINA 20MG/1ML INJ - GENTAMICIN" : "INTERMEDIARIO",
        "GENTAMICINA 40MG (40MG/ML) AMP 1ML INJ - GARAMICINA" : "INTERMEDIARIO",
        "GENTAMICINA 80MG (40MG/ML) AMP 2ML INJ - GARAMICINA" : "INTERMEDIARIO",
        "GENTAMICINA 80MG INJ. AMPOLA C/ 2ML" : "INTERMEDIARIO",
        "GENTAMICINA 40MG INJ. AMP. 1 ML" : "INTERMEDIARIO",
        #IVERMECTINA
        "IVERMECTINA 6MG COMP - LEVERCTIN" : "OUTROS",
        #ERITROMICINA
        "LACTOBIONATO ERITROMICINA FA 1000MG PO SOL INFUS - TROMAXIL" : "OUTROS",
        #LEVOFLOXACINO
        "LEVOFLOXACINO 500MG (5MG/ML) BOLSA 100ML INJ - TAVANIC" : "OUTROS",
        "LEVOFLOXACINO 500MG COMP REV - LEVAQUIN" : "OUTROS",
        "LEVOFLOXACINO 750MG COMP REV - TAMIRAM" : "OUTROS",
        "LEVOFLOXACINO HEMI-HIDRATADO 750MG (5MG/ML) BOLSA 150ML" : "OUTROS",
        "LEVOFLOXACINO 500MG INJ. - 100ML" : "OUTROS",
        "LEVOFLOXACINO 500 MG CP. (A)" : "OUTROS",
        "LEVOFLOXACINO 250 MG CP. (A)" : "OUTROS",
        #LINEZOLIDA
        "LINEZOLIDA 600MG (2MG/ML) BOLSA 300ML SOL INF - ZYVOX" : "MMR",
        "LINEZOLIDA 600MG IV INJ. 300ML" : "MMR",
        #MEROPENEM
        "MERONEM FA 1G (1000 MG) PO INJ - MEROPENEM" : "MMR",
        "MEROPENEM 1G FA 1000MG PO SOL INJ IV - MERONEM" : "MMR",
        "MEROPENEM FA 500MG PO SOL INJ - MERONEM" : "MMR",
        "MEROPENEM 1G INJ." : "MMR",
        #METRONIDAZOL
        "METRONIDAZOL 250MG COMP - FLAGYL" : "INTERMEDIARIO",
        "METRONIDAZOL 400MG COMP - FLAGYL" : "INTERMEDIARIO",
        "METRONIDAZOL 500MG (5MG/ML) FR 100ML SOL INJ IV - FLAGYL" : "INTERMEDIARIO",
        "METRONIDAZOL 500 MG INJ. - 100 ML (A)" : "INTERMEDIARIO",
        "METRONIDAZOL 250MG CP. (A)" : "INTERMEDIARIO",
        "METRONIDAZOL 40MG/ML SUSP. C/ 100ML" : "INTERMEDIARIO",
        "METRONIDAZOL 400MG CP. (A)" : "INTERMEDIARIO",
        #MICAFUNGINA
        "MICAFUNGINA SODICA FA 100MG PO LIOF INF IV - MYCAMINE" : "ANTIFUNGICO",
        "MICAFUNGINA SODICA FA 50MG PO LIOF INF IV - MYCAMINE" : "ANTIFUNGICO",
        "MICAFUNGINA 50MG INJ" : "ANTIFUNGICO",
        #MICONAZOL
        "DAKTARIN 20MG/G TB 40G GEL ORAL - MICONAZOL" : "TOPICO",
        "MICONAZOL (20MG/G) TB 40G GEL ORAL - DAKTARIN" : "TOPICO",
        #MOXIFLOXACINO
        "MOXIFLOXACINO 400MG (1,6MG/ML) BS 250ML SOL - AVALOX" : "OUTROS",
        "MOXIFLOXACINO 400MG COMP - AVALOX" : "OUTROS",
        "MOXIFLOXACINO (5,45MG/ML) FR 5ML SOL OFT - VIGAMOX" : "TOPICO",
        "MOXIFLOXACINO + FOSF DEXAMETASONA FR 5ML SOL OFT - VIGADEXA" : "TOPICO",
        "VIGAMOX 5,45MG/ML FR 5ML SOLUCAO OFTALMICA - MOXIFLOXACINO" : "TOPICO",
        #CLORANFENICOL
        "KOLLAGENASE + CLORANFENICOL TB 30G (CLORANFENICOL) " : "OUTROS",
        "RETINOL+AMINOAC+METIONINA+CLORANFE TB3,5G POM OFT - EPITEZAN" : "OUTROS",
        "CLORANFENICOL 1G INJ. (A)" : "OUTROS",
        #MUPIROCINA
        "MUPIROCINA 2% (20MG/G) TB 15G POMADA - BACTROBAN" : "PROFILATICO",
        #NEOMICINA
        "NEOMICINA+BACITRACINA (5MG+250UI/GR) TB 15G POM - NEBACETIN" : "TOPICO",
        "DEXAMETASONA+NEOMICINA+POLIMIXINA B FR 5ML SUSP OFT-MAXITROL" : "TOPICO",
        "TRIANCINOLONA+NEOMICINA+ASSOC TB 30G POMADA-OMCILON A M " : "TOPICO",
        #SULFADIAZINA
        "NITRATO CERIO 0,4%+SULFADIAZINA 1% TB 50G CREM - DERMACERIUM" : "TOPICO",
        "NITRATO CERIO 0,4%+SULFADIAZINA 1% TB 50G CREME-DERMACERIUM" : "TOPICO",
        "SULFADIAZINA PRATA (10MG/G) TB 50G CREME DERM - SILGLOS" : "TOPICO",
        "SULFADIAZINA PRATA 1% (10MG/GR) PT 400GR - DERMAZINE" : "TOPICO",
        "SULFADIAZINA PRATA 1% (10MG/GR) TB 30GR - DERMAZINE" : "TOPICO",
        "SULFADIAZINA 500MG CP.(A)" : "TOPICO",
        #NISTATINA
        "NISTATINA100.000UI/ML FR 50ML SUSPENSAO ORAL - NEO MISTATIN" : "TOPICO",
        "NISTATINA (100.000UI/ML) SER 10ML (R)" : "TOPICO",
        "NISTATINA 100.000UI/ML SER 10ML (R)" : "TOPICO",
        "NISTATINA CREME BISNAGA (25.000UI/G) TB 60G" : "PROFILATICO",
        "NISTATINA 100000UI+OXIDO ZINCO 200MG/G TB 60G POM - DERMODEX" : "PROFILATICO",
        "NISTATINA 100.000 UI/ML SUSP. C/ 50ML (A)" : "TOPICO",
        #NITROFURANTOÍNA
        "NITROFURANTOÍNA 100MG CAPS (A)" : "COMUNITARIO",
        #OXACILINA
        "OXACILINA SODICA FA 500MG PO SOL INJ - OXANON" : "COMUNITARIO",
        "OXACILINA 500MG INJETÁVEL" : "COMUNITARIO",
        #PIPERACILINA_TAZOBACTAM
        "PIPERACILINA+TAZOBACTAM 2,25 (2G+250MG) PO LIO INJ - TAZOCIN" : "HOSPITALAR",
        "PIPERACILINA + TAZOBACTAM (4G/500MG) FA PO LIOF INJ -TAZOCIN" : "HOSPITALAR",
        "PIPERACILINA + TAZOBACTAM 4,5G IV INJ." : "HOSPITALAR",
        "PIPERACILINA 4 G + TAZOBACTAM 500MG IV INJ." : "HOSPITALAR",
        #PIRIMETAMINA
        "PIRIMETAMINA 25MG CP. (A)" : "OUTROS",
        #POLIMIXINAB
        "BEDFORDPOLY-B 500.000 UI PO LIOFILO INJ - POLIMIXINA B" : "MMR",
        "POLIMIXINA B BASE FA 500.000 UI PO LIOF INJ - BEDFORDPOLY-B" : "MMR",
        "POLIMIXINA B BASE FA 500.000 UI PO LIOF INJ - SPOX" : "MMR",
        "SULFATO DE POLIMIXINA B 500.000 UI INJ." : "MMR",
        "COLISTINA BASE 160 MG (A)(COLESTIMETATO 2.000.000UI)" : "MMR",
        #RIFAMPICINA
        "RIFAMPICINA 300MG CAPS DURA - RIFALDIN" : "OUTROS",
        "RIFAMPICINA 150MG+ISONIAZIDA 75MG+PIRAZINAMIDA 400MG + ETAMBUTOL 275MG" : "OUTROS",
        "RIFAMPICINA 300MG CAP. (A)" : "OUTROS",
        "RIFAMPICINA 150MG+ISONIAZIDA 75MG" : "OUTROS",
        "RIFAMPICINA 300MG+ISONIAZIDA 150MG" : "OUTROS",
        "DICLORIDRATO DE ETAMBUTOL 400MG" : "OUTROS",
        #SULFAMETOXAZOL_TRIMETOPRIM
        "SULFAMETOXAZOL 400MG + TRIMETOPRIMA 80MG COMP - BACTRIM" : "OUTROS",
        "SULFAMETOXAZOL 800MG + TRIMETOPRIMA 160MG CAPS - BACTRIM" : "OUTROS",
        "SULFAMETOXAZOL 800MG + TRIMETOPRIMA 160MG COMP - BACTRIM" : "OUTROS",
        "SULFAMETOXAZOL+TRIMETOPRIM (200MG+40MG/5ML) FR 100ML BACTRIM" : "OUTROS",
        "SULFAMETOXAZ+TRIMETOPRIMA (400+80MG/5ML) INJ - BAC SULFITRIN" : "OUTROS",
        "SULFAMETOXAZOL +TRIMETOPRIMA (400MG+80MG) INJ.- 5ML (A)" : "OUTROS",
        "SULFAMETOXAZOL+TRIMETOPRIMA (200MG+ 40MG/5ML) SUSP. ORAL PED. 100ML" : "OUTROS",
        "SULFAMETOXAZOL TRIMETOPRIMA F (800+160MG) CP. (A)" : "OUTROS",
        "SULFAMETOXAZOL + TRIMETROPIMA (400MG + 80MG) CP. (A)" : "OUTROS",
        #TAMIFLU
        "TAMIFLU 75MG CAPS." : "COMUNITARIO",
        "TAMIFLU 30MG CAPS." : "COMUNITARIO",
        "TAMIFLU 45MG CAPS." : "COMUNITARIO",
        #TEICOPLANINA
        "TEICOPLANINA FA 200MG PO LIOF INJ - TARGOCID" : "MMR",
        "TEICOPLANINA FA 400MG PO LIOF INJ - TARGOCID" : "MMR",
        #TETRACICLINA
        "TETRACICLINA 500MG CAP. (A)" : "COMUNITARIO",
        #TOBRAMICINA 
        "TOBRAMICINA (3MG/ML) FR 5ML SOL OFT - TOBREX" : "TOPICO",
        #VANCOMICINA
        "VANCOMICINA FA 500MG PO INJ - VANCOCINA" : "HOSPITALAR",
        "CLORIDRATO DE VANCOMICINA 500MG  INJ. (A)" : "HOSPITALAR",
        #VORICONAZOL
        "VORICONAZOL 200MG COMP REV - VFEND" : "ANTIFUNGICO",
        "VORICONAZOL IV FR 200MG PO SOL INF - VFEND" : "ANTIFUNGICO",
        "VORICONAZOL IV FR 200MG PO SOL INF - VFEND IV" : "ANTIFUNGICO",
    }
    
    c["atb"] = c["atb"].apply(lambda x: translate_atb[str(x).strip().upper()] if str(x).upper().strip() in translate_atb.keys() else 'OUTROS')
    
    desejos = ['COMUNITARIO', 'TOPICO', 'INTERMEDIARIO',
        'HOSPITALAR', 'MMR', 'ANTIFUNGICO', 'OUTROS', 'PROFILATICO'
    ]
    c = maestro.create_dummy_vectorized(df= c,column= "atb", arrayDeDesejos= desejos)

    categ_atb = {
        'COMUNITARIO': 1,
        'PROFILATICO': 1,
        'OUTROS': 2,
        'TOPICO': 3,
        'INTERMEDIARIO': 4,
        'HOSPITALAR': 5,
        'MMR': 6,
        'ANTIFUNGICO': 6
    }

    c["atb_importancia"] = c["atb"].map(categ_atb).fillna(0).astype(int)

    #-------------pivot de vias passado---------
    #translate_via = {
    #    'VV': "PARENTERAL",
    #    'EV': "PARENTERAL",
    #    'IV': "PARENTERAL",
    #    'EVB': "PARENTERAL",
    #    'IN': "PARENTERAL",
    #    'IM': "PARENTERAL",
    #    'TO': "TOPICO",
    #    'OF': "TOPICO",
    #    'AO': "TOPICO",
    #    'HIP': "OUTRO",
    #    'SC': "OUTRO",
    #    'BE': "OUTRO",
    #    'JN': "ENTERAL",
    #    'TQ': "ENTERAL",
    #    'GT': "ENTERAL",
    #    'SGA': "ENTERAL",
    #    'SEN': "ENTERAL",
    #    'VO': "ENTERAL",
    #}
    #c['via'] = c['via'].apply(lambda x: translate_via[str(x).strip().upper()] if str(x).strip().upper() in translate_via.keys() else "OUTRO")
    #desejos = ['PARENTERAL', 'TOPICO', 'ENTERAL']#, 'OUTRO']
    #c = maestro.create_dummy_vectorized(df= c,column= "via",  arrayDeDesejos= desejos)

    #------tradução de vias nova --------
    translate_via = {
        # 
        'VV': 4,
        'EV': 4,
        'INTRAVENOSA INFUSÃO ESTENDIDA': 4,
        'INTRAVENOSA INFUSÃO': 4,
        'INTRAVENOSA DIRETO': 4,
        'IV': 4,
        'EVB': 4,
        # 
        'IN': 3,
        'IM': 3,
        'INTRAMUSCULAR': 3,
        # 
        'TO': 1,
        'TÓPICO': 1,
        'USO EXTERNO': 1,
        'OF': 1,
        'AO': 1,
        'HIP': 1,
        'SC': 1,
        'SUBCUTÂNEA': 1,
        'BE': 1,
        'INTRAPLEURAL': 1,
        # 
        'JN': 2,
        'TQ': 2,
        'GT': 2,
        'SGA': 2,
        'SEN': 2,
        'VO': 2,
        'ORAL': 2,
        'SONDA NASOENTERAL': 2,
        'SONDA NASOGASTRICA': 2,
        'SONDA NASOGÁSTRICA': 2,
        'OROGÁSTRICA': 2,
        'ENTERAL': 2,
        'GASTROSTOMIA': 2,
    }
    c["via_importancia"]= c["via"].str.strip().str.upper().map(translate_via).fillna(0).astype(int)

    colunas = ["registro", "cd_pre_med"]
    c = maestro.to_int(df= c, arrayColumns= colunas)

    tuplas = [(",", ".")]
    c = maestro.replace_values_list(df= c, column= "dose", arrayDeTuplas= tuplas)

    colunas = [
        "prescription_date",
        "atb"
    ]
    c = maestro.remove_columns(df= c, arrayColumns= colunas)
    
    novosNomes = {
        "atb_copy": "atb",
    }
    c = maestro.rename_columns(df= c, DictColumns= novosNomes)

    dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "imparare2_prescricoesantibiotico_prepared", if_exists=  "append")

def main():
    replace =True
    if replace:
        create_query = """
            DROP TABLE IF EXISTS imparare2_prescricoesantibiotico_prepared;

            CREATE UNLOGGED TABLE IF NOT EXISTS imparare2_prescricoesantibiotico_prepared (
                registro INTEGER,
                dthr_prescricao TIMESTAMP,
                atb TEXT NULL,
                dose TEXT NULL,
                unidade TEXT NULL,
                frequencia TEXT NULL,
                via TEXT NULL,
                via_importancia INTEGER NULL,
                atb_importancia INTEGER NULL,
                "atb_COMUNITARIO" INTEGER NULL,
                "atb_TOPICO" INTEGER NULL,
                "atb_INTERMEDIARIO" INTEGER NULL,
                "atb_HOSPITALAR" INTEGER NULL,
                "atb_MMR" INTEGER NULL,
                "atb_ANTIFUNGICO" INTEGER NULL,
                "atb_OUTROS" INTEGER NULL,
                "atb_PROFILATICO" INTEGER NULL,
                attendance_type TEXT NULL,
                id_enterprise SMALLINT
            );

            CREATE INDEX IF NOT EXISTS idx_imparare2_prescricoesantibiotico_prepared ON imparare2_prescricoesantibiotico_prepared (id_enterprise, registro, date(dthr_prescricao));
        """
        dataRequest.execute(queryText= create_query)

    append_query = f"""
        SELECT
            registro AS registro,
            prescription_date AS dthr_prescricao,
            atb AS atb,
            MAX("DOSE")::text AS dose,
            MAX("UNID") AS unidade,
            MAX("FREQUENCIA") AS frequencia,
            MAX("VIA") AS via,
            'I' AS attendance_type, 
            id_enterprise
        FROM(
            SELECT
                p.record_id AS registro,
                prescription_date AS prescription_date,
                antibiotic AS atb,
                FIRST_VALUE(dosage) OVER (PARTITION BY p.record_id, h.id_enterprise, prescription_date, antibiotic ORDER BY prescription_date ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS "DOSE",
                FIRST_VALUE(antibiotic_unity) OVER (PARTITION BY p.record_id, h.id_enterprise, prescription_date, antibiotic ORDER BY prescription_date ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS "UNID",
                FIRST_VALUE(frequency) OVER (PARTITION BY p.record_id, h.id_enterprise, prescription_date, antibiotic ORDER BY prescription_date ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS "FREQUENCIA",
                FIRST_VALUE(via) OVER (PARTITION BY p.record_id, h.id_enterprise, prescription_date, antibiotic ORDER BY prescription_date ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS "VIA",
                h.id_enterprise
            FROM prescriptions p
            inner join hospitals h
            	on p.id_hospital = h.id_hospital 
            INNER JOIN patients_to_update ptu
                on ptu.record_id = p.record_id
                    AND h.id_enterprise = ptu.id_enterprise
        ) p
        GROUP BY registro, id_enterprise, prescription_date, atb;
    """

    df_iterator = dataRequest.get_data(queryText= append_query, chunck = 2000)
    with Pool(processes= cpu_count()) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass

if __name__ == "__main__":
    main()