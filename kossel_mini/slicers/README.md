# Fatiadores — Kossel Mini + Dragon Burner

Perfis do OrcaSlicer para a Kossel Mini com o toolhead Dragon Burner (BLTouch `left`) e Marlin 2.1.2.9. Calibração e firmware estão no [README da impressora](../REAME.md).

![Mesa no OrcaSlicer](orcaslicer/preview.png)

## Arquivos

| Caminho | O que é |
|---|---|
| `orcaslicer/machine/Kossel Mini Dragon Burner 0.4.json` | Impressora: mesa circular de Ø210, G-code inicial/final, retração, limites do firmware |
| `orcaslicer/process/0.12mm Fine @Kossel Dragon Burner.json` | Processo 0.12mm |
| `orcaslicer/process/0.20mm Standard @Kossel Dragon Burner.json` | Processo 0.20mm |
| `orcaslicer/process/0.28mm Extra Draft @Kossel Dragon Burner.json` | Processo 0.28mm |
| `orcaslicer/process/0.20mm Calibração @Kossel Dragon Burner.json` | Processo para peças de calibração: o 0.20 sem saia e com paredes a 40mm/s |
| `orcaslicer/kossel_dragon_burner_bed.svg` | Textura da mesa: zonas das torres em vermelho, fundo transparente |
| `orcaslicer/kossel_dragon_burner_plate.stl` | Modelo 3D da placa redonda (Ø216) |
| `orcaslicer/preview.png` | Prévia da mesa (imagem acima) |
| `orcaslicer/install.sh` | Instala os perfis no OrcaSlicer (Linux) |

## Mesa

A área imprimível é o círculo inteiro de Ø210 (origem no centro, altura máxima 115mm). O firmware aceita esse círculo e **não protege as torres**: o BLTouch encostou na correia da torre X com o bico em r≈90. As zonas em vermelho são onde a cabeça chegaria a menos de 10mm de uma correia:

| Direção | O bico pode ir até (do centro) |
|---|---|
| Torre X (frente-esquerda, lado do BLTouch) | 74,5mm |
| Torre Y (frente-direita) | 83mm |
| Torre Z (trás) | 92mm |
| Entre as torres | 105mm (borda da mesa) |

**O vermelho é só visual: o Orca não impede peças nessas zonas.** Testado: um cubo dentro da zona da torre X fatia normalmente (e bateria na correia). Então:
- Posicione as peças, a saia e o brim fora do vermelho.
- O **Arrange** (tecla A) não conhece as zonas e pode colocar peças nelas: confira depois de organizar.
- Uma área imprimível recortada no formato das zonas não resolveria: o Orca só verifica o contorno externo de áreas não convexas, e testado assim ele também deixa passar peças no recorte.

O estilo segue a mesa da Voron no Orca: placa escura com a grade do próprio Orca, textura transparente com o vermelho `#fe0000` e o cinza `#bcbec0`.

## Instalar no OrcaSlicer

Testado no OrcaSlicer 2.4.2 (flatpak). Os perfis herdam dos modelos `MyMarlin 0.4 nozzle` e `@MyMarlin` que vêm com o próprio Orca (vendor "Custom").

### Linux

```bash
cd kossel_mini/slicers/orcaslicer
./install.sh                     # detecta o flatpak ou ~/.config/OrcaSlicer
./install.sh /caminho/OrcaSlicer # outra pasta de configuração
```

Se você estiver logado no Orca, os perfis ficam em `user/<seu id>` em vez de `user/default`:

```bash
ORCA_USER_DIR=~/.var/app/com.orcaslicer.OrcaSlicer/config/OrcaSlicer/user/<id> ./install.sh
```

O script copia os JSON, cria os `.info` e aponta a textura e o modelo da placa para este repositório (eles não são copiados: se mover o repositório, rode o script de novo). Depois **reinicie o Orca**, selecione a impressora **Kossel Mini Dragon Burner 0.4** e um dos processos `@Kossel Dragon Burner`.

### Outros sistemas (manual)

1. **File → Import → Import Configs...** e selecione os 4 JSON (`machine/` e `process/`).
2. **Printer settings → Basic information → Bed shape**: em **Texture → Load** escolha `orcaslicer/kossel_dragon_burner_bed.svg` e em **Model → Load** escolha `orcaslicer/kossel_dragon_burner_plate.stl`.

### Conferir depois de instalar

1. A mesa aparece redonda, com as zonas vermelhas na frente-esquerda (X, a maior), na frente-direita (Y) e atrás (Z), como na prévia.
2. Escolha o tipo de mesa (**Plate type**, acima da mesa): **Smooth PEI Plate / High Temp Plate** ou **Textured PEI Plate**, conforme o seu PEI. O Orca guarda a escolha por impressora, e a temperatura da mesa sai do filamento conforme esse tipo.

## Impressora

| Configuração | Valor |
|---|---|
| G-code | `marlin2`, extrusão relativa (`M83`) com `G92 E0` a cada camada |
| Retração | 2,8mm a 55mm/s, retorno a 35mm/s, wipe 0,5mm, z-hop 0,4mm só em superfícies de topo |
| Limites da máquina | Os do firmware (acel. 3000, impressão 1500, deslocamento 3000, retração 5000, E 500, jerk 10 / E 1,5); `emit_machine_limits_to_gcode` desligado: servem só para estimar o tempo |

A retração veio do perfil antigo da Kossel (bowden, mesmo extrusor); vale refazer o teste de retração do Orca (**Calibration → Retraction test**) com o hotend do Dragon Burner.

G-code inicial:

```gcode
G90
M83
M140 S[bed_temperature_initial_layer_single]
G28
M190 S[bed_temperature_initial_layer_single]
G33 O P1                  ; recalibra a altura com o probe no centro da mesa (faz o homing)
M420 S0                   ; sem malha: fora do centro o probe não acompanha a altura do bico
G1 X-30 Y-80 Z10 F3000    ; espera o bico aquecer fora da área das peças
M104 S[nozzle_temperature_initial_layer]
M109 S[nozzle_temperature_initial_layer]
G92 E0
G1 X-30 Y-80 Z0.3 F3000   ; purga na frente, fora de peças de até 140 mm e longe das torres
G1 X30 Y-80 E12 F1000
G92 E0
G1 Z2 F3000
```

Com a mesa já quente, o `G33 O P1` mede o centro e recalcula a altura. A mesa é fixa (sem molas) e a leitura do probe fica estável desde o primeiro minuto a 50 °C, então não precisa esperar depois do `M190`.

O gcode não usa malha (`G29`). Fora do centro, a leitura do BLTouch não acompanha a altura do bico: com a geometria calibrada, o probe ainda lê o fundo e o lado esquerdo 0,4 a 0,6 mm acima do centro, e a malha levantava o bico ali (na peça de calibração de 2026-11-04, os pilares do fundo e o da torre Y ficaram longe da mesa). Se voltar a usar o `G29`, não troque os limites `L-80 R70 F-90 B80` sem refazer a conta de folga (ver o README da impressora): com a área de Ø210, um `G29` sem limites ou com outra grade pode levar a cabeça até a correia.

## Processos

Comum aos três: aceleração 1500 (paredes externas e topo 1000, primeira camada 500, deslocamento 3000, pontes 50%), deslocamento a 150mm/s, saia de 1 volta a 5mm, costura alinhada, arc fitting desligado (o Marlin segmenta arcos na delta).

| | 0.12mm Fine | 0.20mm Standard | 0.28mm Extra Draft |
|---|---|---|---|
| Primeira camada | 0,20mm | 0,25mm | 0,30mm |
| Paredes | 3 | 3 | 2 |
| Topo / fundo | 6 / 5 | 4 / 3 | 3 / 3 |
| Preenchimento | 15% gyroid | 15% gyroid | 12% grid |
| Parede externa / interna | 40 / 70mm/s | 50 / 90mm/s | 50 / 90mm/s |
| Preenchimento / sólido | 90 / 70mm/s | 110 / 90mm/s | 110 / 90mm/s |
| Topo | 40mm/s | 50mm/s | 50mm/s |
| Primeira camada | 20mm/s | 25mm/s | 25mm/s |

**0.20mm Calibração**: igual ao 0.20 instalado, mas sem saia (a saia a 5mm de uma peça de 140mm passaria do limite da torre X) e com paredes, topo e sólido a 40mm/s e preenchimento a 60mm/s. Feito para a peça de calibração do Klipper (`calibrate_size.stl`), que pede ~40mm/s.

A purga fica em Y=−80, de X=−30 a 30: a 10mm de uma peça de 140mm centrada e com projeção de 66mm nas direções das torres X e Y (limites 74,5 e 83). Antes ela ficava em Y=−55, por cima da base de peças com mais de ~110mm.

Velocidades para as guias MGN, cerca do dobro das dos patins antigos. No 0.20, um cubo de 20mm cai de 29min43s para 21min29s e uma caixa de 60×60×10mm de 1h31 para 1h01 (estimativa do Orca com o PLA genérico).

O que limita daqui para cima:
- **Vazão do filamento**: o PLA genérico do Orca limita a 12mm³/s; no 0.28, o preenchimento a 110mm/s passa disso e o Orca reduz sozinho.
- **Peças pequenas**: o tempo mínimo por camada do filamento (4s no PLA genérico) e a aceleração em segmentos curtos (curvas do gyroid) seguram a velocidade; subir as velocidades quase não muda um cubo de 20mm.
- **Placa AVR com 1/32 de micropasso**: numa delta o Mega segmenta cada movimento; acima de ~150mm/s podem aparecer travadinhas. Para ir além, o caminho é 1/16 de micropasso (80 passos/mm) ou uma placa 32 bits.

## Filamento

Os perfis não incluem filamento: use os genéricos do Orca (`Generic PLA @System`, `Generic PETG @System`...) ou os seus. A temperatura da mesa sai do filamento conforme o tipo de mesa; o PLA genérico usa 45°C em PEI, ajuste no perfil do filamento se preferir mais.

## Atualizar os perfis

Ao mudar um perfil no Orca, copie os JSON de volta de `~/.var/app/com.orcaslicer.OrcaSlicer/config/OrcaSlicer/user/default/machine/` e `.../process/` para `orcaslicer/`. Os caminhos da textura e do modelo podem ficar como estiverem: o `install.sh` reescreve.

## Outros fatiadores

A textura tem 210×210mm em escala real e serve em qualquer fatiador com mesa circular de Ø210 e origem no centro (no PrusaSlicer: **Printer Settings → General → Bed shape → Texture**).
