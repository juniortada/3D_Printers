## Voron 2.4 250/300/350
### Guia completo com todos as medidas oficiais.
  - https://vorondesign.com/voron2.4

## Guia de compras para montagem de uma versão "baixo custo"

### Frame
  ##### Perfil de alumínio 20x20 pode ser encontradado na forseti, cncparts e aliexpress.
  Atualmente o preço não compensa comprar no aliexpress. Fica mais barato comprar peças inteiras
  e cortar mas você já pode solicitar as peças nas medidas da impressora.
  Para cortar precisa de ferramentas para fazer corte com precisão, além de furos e rosca.
  - https://loja.forsetisolucoes.com.br/produto/perfil-estrutural-em-aluminio-20x20-t-slot-canal-6/
  - https://www.mercadolivre.com.br/perfil-de-aluminio-v-slot-20x20-1-peca-x-1200-mm/p/MLB2072566857

  ##### Parafusos, arruelas e porcas M3 e M5 tamanhos variados(verificar lista oficial), pode ser comprado em qualquer loja de ferragens.
  Não precisa ser inox que custa muito mais caro, apenas zincado ou preto.
  Porca v-slot (porca que trava parafuso no pefil de alumínio) tanto M3 como M5
  só utilizei em partes realmente estruturais, para prender skirt, painéis, etc eu imprimir os adaptadores para porcas normais.
  - https://www.thingiverse.com/thing:1073567
  - https://www.thingiverse.com/thing:5155562
  - https://www.thingiverse.com/thing:161023

  ##### Guias lineares podem ser encontradas na forseti, cncparts e aliexpress.
  O preço e disponibilidade varia, verifique as medidas no guia oficial de acordo com o seu modelo
  - https://pt.aliexpress.com/item/1005005462898522.html
  - https://loja.forsetisolucoes.com.br/produto/guia-linear-mgn-series-9mm-12mm-15mm-aco-s55c/

  ##### Correias e polias
  Pode ser encontrando no mercadolivre ou aliexpress, verifique as medidas no guia oficial.
  O preço e a disponibilidade varia, assim como frete. Existem kit's no aliexpress.
  Cuidado com o preço do frete se comprar pulverizado entre vários fornecedores.
  Os rolamentos necessários são facilmente encontrados em lojas físicas especializadas.
  - https://pt.aliexpress.com/item/1005004142186208.html

  <img width="940" height="541" alt="Captura de tela de 2026-05-14 14-18-26" src="https://github.com/user-attachments/assets/79308dda-f1f8-410a-8819-b67f2a6a40c2" />


  Dica importante, as polias 80T que são as mais caras NÃO precisam ser de aluminio
  (na verdade nenhuma precisa, é fácil encontrar todos os modelos no thingiverse),
  podem ser impressas, estou utilizando impressas no extrussor, as outras eu já tinha de alumínio. 
  No manual de montagem do extrusor Mobius M4 é recomendado "recortar" uma polia 20T
  de alumínio, mas essa também pode ser impressa, inclusive é mais fácil de "recortar"
  para conectar na polia 80T.
  Recomendo a "versão" do extrusor Voron Mobius M4, é mais bonita que a "versão" da 2.4
  - https://github.com/VoronDesign/Mobius-Extruder/blob/m4/STLs/%5Ba%5D_80t_gear.stl
  - https://www.thingiverse.com/thing:1142810
  - https://github.com/VoronDesign/Voron-2/blob/Voron2.4/STLs/Superceded_Parts/%5Ba%5D_stopgap_80T_hubbed_gear.stl

### Eletronica
Atualmente estou utilizando fonte 12v, mas já vou fazer upgrade para 24v.
Pode ser comprado no mercado livre/loja de materiais elétricos. Somente exemplo, procure a com frete grátis ou loja física.
 - https://www.mercadolivre.com.br/kit-especial-para-vacinahotbh/p/MLB2052813762
 - https://www.mercadolivre.com.br/fonte-de-alimentacao-chaveada-ms-400w-24v-166a-bivolt/up/MLBU2863288042
  
  ##### Motherboard
  Aqui vai um observação importante, você NÃO precisa de um raspeberry pi se for instalar Marlin 2.
  Isso não quer dizer que eu recomendo, atualmente minha impressora está funcionando muito bem assim,
  mas já estou com planos de migrar para Klipper com um raspberry pi 2 1gb.
  Caso não tenha um raspberry pi, recomendo um Orange pi que custa muito menos.
  MKS Monster 8 V2 + driver TMC 2209, vou colocar link do aliexpress mas o preço pode variar, procure 
  o vendedor com melhor cotação no dia.
  - https://pt.aliexpress.com/item/1005005571907852.html

  <img width="454" height="395" alt="Captura de tela de 2026-05-14 16-07-42" src="https://github.com/user-attachments/assets/373a599f-177c-45b9-a5f0-64933cf7d7b5" />

  
  Aqui vai outra dica importante, com a monster 8 você já controla todos os motores + dois extrusores, 
  sem precisar de uma ebb ou placa adicional.
  Na recomendação da documentação oficial: duas Bigtreetech skr v1.4 ou Bigtreetech Octopus + raspberry pi 4.
  Sem contar o raspberry, somente as placas, elas custam o dobro de uma MKS Monster 8.
  Você também  não precisa de driver TMC 2209 nos extrusores, mas é uma economia tão pequena que não vale a pena.
  Agora o display LCD faz muita diferença na economia, dependendo do modelo será quase o preço da própria
  placa ou de um orange pi. Um mini12864 já serve. Até um de ramps serve, mas o mini12864 é mais bonito e custa pouco, exemplo:
  - https://pt.aliexpress.com/item/1005007505557471.html
  - https://pt.aliexpress.com/item/1005009393017580.html

  ##### Mesa aquecida
  SSR 40a para alimentar a mesa aquecida. Pode ser encontrado no mercadolivre/aliexpress. 
  O preço é baixo, procure alguma opção com frete grátis e dissipador de calor incluso.
  Com dissipador apropriado não precisa de fan. 
  - https://www.mercadolivre.com.br/rele-de-estado-solido-ssr-controle-ac-110v-220v-40a/up/MLBU2207562163

  Aquecedor 110v/220v. Pode ser encontrado no aliexpress, procure a versão adequada para o seu tamanho.
  Link da versão para voron 300.
  - https://pt.aliexpress.com/item/1005004637214388.html

  Mesa de alumínio pode ser uma chapa 3~4mm. Não precisa ser retificada,
  a que comprei no mercado livre estava em boa qualidade (plana).
  Comprei uma medida com folga para cortar e dar acabamento nas bordas.
  - https://www.mercadolivre.com.br/chapa-aluminio-4mm-x-35cm-x-35cm/up/MLBU778761923
  
  Os modelos retificados no aliexpress tem preço muito elevado.

  Para nivelamento automático da mesa estou utilizando BlTouch, mas somente porque já tinha.
  O Klicky Probe e suas variantes fica mais barato, você pode montar o hardware ou
  comprar pronto no aliexpress. O BlTouch é mais prático por não precisar configurar docking.
  A precisão na minha impressora está relativamente boa.
  - https://pt.aliexpress.com/item/32958675206.html
  - https://github.com/jlas1/Klicky-Probe
  - https://pt.aliexpress.com/item/1005005023158174.html

  A placa PEI + manta magnética pode ser um modelo "barato", no meu caso eu não economizei 
  e comprei uma cryogrip BIQU, mas não é um gasto que vai fazer muita diferença.
  Compre no aliexpress.
  Usei por muito tempo mesa de vidro sem PEI. Verifique a medida da sua impressora.
  Mas CUIDADO, antes de comprar verifique se inclui a base magnetica.
  - https://pt.aliexpress.com/item/1005004569503247.html (base incluida)
  
  Sem a base magnética (precisa ser comprado a parte).  
  - https://pt.aliexpress.com/item/1005008578258312.html
  - https://pt.aliexpress.com/item/1005008158165231.html

  ##### Motores
  Montei com nema 17 17HS4401, não são os recomendados, mas funcionam.
  Usei em todos os eixos, inclusive nos extrusores.
  Pode ser tanto do mercado livre como aliexpress, verifique frete e taxas.
  - https://pt.aliexpress.com/item/1005008459399126.html
  - https://www.mercadolivre.com.br/motor-de-passo-nema-17-de-42kgf-para-impressora-3d/up/MLBU1748960636
  
  Dica importante, utilize ventilação forçada e baixa corrente nos x/y (A/B do gantry), como são de baixa qualidade
  aquecem com facilidade. Estou utilizando corrente de 900. Ajuste esse valor para não perder passos
  e fique de olho no aquecimento dos motores.
  Link de adaptador de fan 4010 para os motores
  - https://www.thingiverse.com/thing:1409754

  ##### EndStops
  Existe o modelo próprio da Voron
  - https://pt.aliexpress.com/item/1005009408301773.html
  
  Estou utilizando sensorless homing no x/y dos drivers TMC 2209,
  mas não é confiável, falha consistentemente. Pode ser a baixa qualidade
  dos motores ou não funciona muito bem no marlin.
  A princípio não queria instalar endstop para reduzir a fiação/zipchain no gantry,
  não por custos já que um endstop físico é barato.
    
    
  ##### HotEnd e Extrusor
  Estou utilizando um clone E3D v6 12v somente porque já tinha também.
  Essa é a economia que estou mais sofrendo até aqui, não acho que vale a pena.
  Vou trocar por hotend Bambu 24v ou E3D REVO 24v.
  Vou deixar o link dos clones mas realmente não indico essa economia. 
  - https://www.mercadolivre.com.br/hotend-v6-e3d-all-metal-bowden-175mm-12v-40w-impressora-3d/p/MLB52904694
  - https://pt.aliexpress.com/item/1005010072331903.html
  - https://pt.aliexpress.com/item/1005005119688537.html

  Extrusor eu testei várias opções:
  StealthBurner bowden + Voron Mobius M4 Extruder
  - https://github.com/VoronDesign/Voron-Stealthburner
  - https://github.com/VoronDesign/Mobius-Extruder

  StealthBurner direct drive + Sherpa Mini
  - https://github.com/Annex-Engineering/Sherpa_Mini-Extruder

  DragonBurner bowden + Voron Mobius M4 Extruder
  - https://github.com/chirpy2605/voron/tree/main/V0/Dragon_Burner

  O kit de hardware vai depender do modelo, Mobius M4 e Sherpa mini tem preço próximo
  de polias/engrenagens mas motores totalmente diferentes. 
  Mobius usa os mesmos nema 17 enquanto que Sherpa usa nema 14 "pancake".

  O hardware do StealthBurner/DragonBurner é somente parafusos e fan's.
  Não esqueça de comprar fan's da mesma voltagem da sua fonte/placa.
  
  DragonBurner
  - 1x 3010 (geralmente vem no E3D)
  - 2x 4010 **blower** version
  
  O StealthBurner também precisa de heat insert m3
  - 1x 4010 (recomendo comprar peças a mais para ventilação x/y, driver, etc)
  - 1x 5015 **Turbina**
  - https://pt.aliexpress.com/item/1005007995311296.html

  ##### Painéis de acrílico
  Pode ser encontrado no mercadolivre ou lojas de corte a laser.
  Caso você tenha equipamento, é realmente fácil de cortar.
  Os laterais/superior é literalmente um quadrado.
  Se for precisar de corte a laser talvez o deck que tem furação/recorte.
  Se a economia for pequena faça o traseiro e das portas com corte a laser para dar maior acabamento.
  3~4mm é suficiente.
  - https://www.mercadolivre.com.br/chapa-placa-acrilico-transparente-50x50cm-3mm/up/MLBU730234773

  Link dos arquivos para corte laser:
  - https://github.com/VoronDesign/Voron-2/tree/Voron2.4/Drawing_DXFs

  ##### Peças impressas
  Caso você não tenha uma impressora, compre somente:
  - conjunto Z de motores + correias.
  - gantry completo (x/y a/b)
  - extrusor completo para o modelo selecioando.
  - heat insert m3 (iguais do StealthBurner)
  -  https://pt.aliexpress.com/item/1005007995311296.html
  
  Gastei aproximadamente 2kg de filamento ABS, imprimi peças sobressalentes,
  mais de um modelo de extrusor, etc.
  Se você tem uma graber/prusa/ender já consegue imprimir essas peças,
  mesmo que não com a qualidade necessária, mas assim que concluir a montagem
  básica, pode re-imprimir as peças na nova impressora com qualidade superior.
  Siga as recomendações de resolução/preenchimento da documentação oficial.

  Saias (skirts), fixadores de paineis, fixadores de fan's, mod's, zipchain, etc,
  podem ser impressos porteriomente com a impressora já trabalhando.
    
    
    
