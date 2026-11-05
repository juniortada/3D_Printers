# Calibração da geometria — Kossel Mini

Ferramentas e dados usados para calibrar a geometria em 2026-11-04 (valores e histórico no [README da impressora](../REAME.md#calibração-atual-2026-11-04-marlin-2129-dragon-burner)). Elas substituem o `G33` completo, que nesta máquina não serve: ver [por que](../REAME.md#por-que-não-usar-o-g33-completo-nem-o-g29).

Python 3 com `numpy`, rodando de dentro desta pasta.

| Arquivo | O que é |
|---|---|
| `delta_model.py` | Modelo da delta: cinemática do Marlin (`M665`/`M666`), máquina real e leitura do probe |
| `klipper_fit.py` | Ângulos das torres e raio a partir das medidas da peça de calibração do Klipper |
| `bed_shift.py` | `H` e `M666` que devolvem as leituras do probe a uma referência depois que a mesa mudou de lugar |
| `probe_7_points.gcode` | Sondagem de referência: centro (2 toques) e 6 pontos a r≈80, mesa a 50 °C, sem malha |
| `first_layer_7_pads.gcode` | Teste de primeira camada: 7 quadrados de 15 mm com uma camada de 0,25 mm, sem malha |
| `data/klipper_2026-11-04.json` | Medidas da peça do Klipper e a geometria com que ela foi impressa |
| `data/bed_shift_2026-11-04.json` | Leituras de antes e depois de tirar as molas da mesa |
| `data/probe_reference.json` | Leituras de referência da calibração atual (mesa fixa) |
| `duplo_2x2/` | Bloco Duplo 2x2 com as medidas de um original, usado para conferir o XY |

## Quando usar cada uma

| Situação | O que fazer |
|---|---|
| Antes de cada impressão | Nada: o gcode inicial do Orca roda `G33 O P1`, que refaz só a altura (`H`) no centro |
| Primeira camada esmagada ou alta por igual na mesa toda | `M851 Z` ([seção 8](../REAME.md#8-z-offset-do-bltouch)) |
| A mesa foi tirada, calçada ou mudou de altura | [Mesa mudou de lugar](#mesa-mudou-de-lugar-bed_shiftpy) |
| Peças em losango ou fora de medida em XY, ou troca de hastes, carros ou torres | [Peça do Klipper](#ângulos-e-raio-peça-do-klipper) e depois os [7 quadrados](#primeira-camada-7-quadrados) |

## Modelo

`delta_model.py` faz a mesma conta do Marlin: torre `i` em `(R·cos(a_i), R·sin(a_i))`, com `a = 210°, 330°, 90°` mais o ajuste de ângulo do `M665 X Y Z`, haste `L` mais o `M665 A B C`, e o carro em home a `H + √(L² − R²) − M666`. Para cada ponto que o firmware manda, ele calcula quanto cada carro desce a partir do home e, com outra geometria (a "máquina real"), onde o bico vai parar de verdade.

A leitura do probe é a diferença entre a altura em que o firmware acha que o bico está e a altura real, com o bico deslocado do ponto sondado pelo offset do BLTouch (X −33,24, Y −10,88). O modelo não tem inclinação do effector nem mesa curva: por isso as previsões de leitura valem para **mudanças** de parâmetro (a diferença entre antes e depois), e não para a leitura absoluta.

Conferido na impressora: ao aplicar os ângulos de 2026-11-04, o probe mudou como o modelo previa, com até 0,11 mm de diferença por ponto (repetibilidade das medidas de controle: 0,15 mm).

| Ponto | Previsto | Medido |
|---|---|---|
| centro | +0,03 | +0,00 |
| torre X | −0,08 | −0,03 |
| torre Y | +0,19 | +0,08 |
| torre Z | −0,45 | −0,40 |
| entre Y-Z | −0,24 | −0,26 |
| entre Z-X | +0,02 | +0,01 |
| frente | −0,04 | −0,09 |

## Ângulos e raio: peça do Klipper

A peça é a do [Enhanced Delta Calibration do Klipper](https://www.klipper3d.org/Delta_Calibrate.html#enhanced-delta-calibration) ([`calibrate_size.stl`](https://raw.githubusercontent.com/Klipper3d/klipper/master/docs/prints/calibrate_size.stl)): um pilar no centro e 6 a 65 mm, nas direções das torres e entre elas. O Klipper faz a conta com `DELTA_ANALYZE`; `klipper_fit.py` reproduz a conversão das medidas em distâncias do Klipper e ajusta o modelo do Marlin.

**Imprimir**
1. No Orca, processo **0.20mm Calibração @Kossel Dragon Burner** (sem saia, paredes a 40 mm/s; ver [slicers](../slicers/README.md#processos)).
2. Peça no centro e sem girar: a letra A fica do lado da torre X (frente-esquerda), B da Y, C da Z.
3. Anote o `M665` e o `M666` da impressora (`M503`) e não mexa neles até medir.

**Medir** com paquímetro, por fora dos pilares. Os pilares externos, na ordem anti-horária vista de cima: A (torre X), far_C (frente), B (torre Y), far_A (fundo-direita), C (torre Z), far_B (fundo-esquerda).

| Campo do JSON | Medidas |
|---|---|
| `center_dists` | Do pilar central a cada externo, na ordem acima (6) |
| `outer_dists` | Entre externos vizinhos: A→far_C, far_C→B, B→far_A, far_A→C, C→far_B, far_B→A (6) |
| `center_pillar_widths` | Largura do pilar central nas direções A, B e C (3) |
| `outer_pillar_widths` | Largura de cada externo, na ordem acima (6) |
| `first_layer` | Opcional: o resultado dos 7 quadrados impressos com a mesma geometria. `nozzle_error_mm` negativo = esmagado. Prende o `M666` para a primeira camada não mudar |
| `printed_with` | `M665` e `M666` com que a peça foi impressa |

**Calcular**

```bash
python3 klipper_fit.py data/klipper_2026-11-04.json --leave-one-out
```

A saída tem a correção de cada parâmetro com a incerteza, o resíduo de cada medida e os comandos `M665`/`M666` para aplicar. Com `--leave-one-out`, refaz a conta tirando uma medida de cada vez: se o resultado pular muito, alguma medida está errada. `--rods` também tenta ajustar as hastes por torre (`M665 A B C`).

Resultado de 2026-11-04:

| | Correção | Incerteza | Sem uma medida de cada vez |
|---|---|---|---|
| Ângulo da torre X | +1,42° | ±0,26° | +1,27° a +1,52° |
| Ângulo da torre Y | +0,49° | ±0,26° | +0,22° a +0,63° |
| Raio | +0,44 mm | ±0,10 mm | +0,36 a +0,51 mm |

Resíduo de 0,30 mm por medida, que é a precisão do paquímetro nessa peça. As hastes por torre não dão para separar: com `--rods` a incerteza delas passa de ±2,4 mm, então ficaram em zero.

**Aplicar** os comandos que o script imprime e `M500`. O `H` não importa, porque o `G33 O P1` do início da impressão refaz. Depois, confira a primeira camada com os 7 quadrados e, se der, reimprima a peça.

## Mesa mudou de lugar (`bed_shift.py`)

Quando a mesa sai do lugar (troca, calço, aperto dos parafusos), a geometria continua certa, mas o `H` e o `M666` não. O script compara as leituras do probe com as da referência (`data/probe_reference.json`, o estado atual, com a primeira camada boa) e calcula o `H` e o `M666` que as devolvem.

1. **Se a mesa mudou mais de ~3 mm de altura**, meça a diferença no centro com a régua (`G28`, `G1 X0 Y0 Z20`) e mude o `H` só na RAM (`M665 H...`) por esse valor antes de sondar. Fora dessa faixa o probe não mede: ele desce no máximo 5 mm abaixo do esperado e falha se tocar mais de 3 mm acima. **Nunca aumente o `H` sem saber que a mesa desceu**: com o `H` maior que o real, o bico desce mais do que o firmware acha.
2. Rode `probe_7_points.gcode` pelo Pronterface. O ponto da torre Y deixa o bico a r=104,6, perto do limite do firmware e a poucos mm da correia; foi conferido com a cabeça montada.
3. Anote as leituras das linhas `Bed X: ... Y: ... Z: ...` (a do centro é a média dos dois toques). Com o console salvo em arquivo, o script faz isso:

   ```bash
   python3 bed_shift.py --parse console.log
   ```

4. Copie `data/probe_reference.json`, troque `measured` pelas leituras novas e pelo `M665`/`M666` com que foram medidas, e rode:

   ```bash
   python3 bed_shift.py data/minha_medida.json
   ```

5. Aplique o `M665 H` e o `M666` impressos, `M500`, e rode a sondagem de novo: as leituras devem ficar a ~0,1 mm da referência. O que sobra é curvatura da mesa, que o `M666` não corrige.

Em 2026-11-04 a mesa desceu entre 8,0 e 8,9 mm ao tirar as molas (`data/bed_shift_2026-11-04.json`):

```bash
python3 bed_shift.py data/bed_shift_2026-11-04.json
# M665 L235.50 R113.15 H151.78 X1.19 Y0.71 Z0.01 ...
# M666 X0.00 Y-1.87 Z-0.40
```

A referência dessa conta era a média de 6 sondagens com a mesa com molas, já estabilizada. A gravada foi `M666 Y−1.86`, da leitura sem arredondar.

## Primeira camada: 7 quadrados

`first_layer_7_pads.gcode` imprime 7 quadrados de 15 mm, com uma camada de 0,25 mm e sem malha: centro, perto de cada torre (r=60: X frente-esquerda, Y frente-direita, Z fundo) e entre elas (frente, fundo-esquerda, fundo-direita). O início segue o do Orca (`G28`, `G33 O P1`, `M420 S0`), com a mesa a 55 °C e o bico a 220 °C. Imprime direto pelo Pronterface em ~5 min.

Olhe cada quadrado: esmagado (transparente, com as linhas fundidas), bom, ou alto (linhas redondas, separadas, pouca aderência). A borda virada para o centro comparada com a de fora mostra prato ou cúpula. Em 2026-11-04, com a geometria atual: os 7 perfeitos.

## Duplo 2x2

`duplo_2x2/duplo_2x2.stl` é um bloco Duplo 2x2 com as medidas de um Duplo original, para conferir o XY com uma peça de encaixe. Impresso em 2026-11-04 com a geometria atual, encaixou macio num original.

Ele substitui um modelo baixado (`Lego+Duplo+2x2_abgerundet.stl`, não incluído) que tinha erros próprios: estava em metros, tinha dois pinos deslocados 0,16 mm (16,16 mm entre eles em vez de 16,00) e todos os diâmetros 0,3 a 0,5 mm maiores que os do original.

| Medida | Modelo baixado | Duplo original | Este |
|---|---|---|---|
| Distância entre pinos | 16,00 / 16,16 | 16,0 | 16,00 |
| Pino (externo / interno) | 9,70 / 7,19 | 9,36 / 6,68 | 9,36 / 6,68 |
| Tubo central (externo / interno) | 13,30 / 11,08 | 12,91 / 10,68 | 12,91 / 10,68 |
| Parede | 1,50 | 1,20 | 1,20 |
| Externo | 31,70 | — | 31,70 |
| Altura (corpo / com pinos) | 19,00 / 23,44 | igual | 19,00 / 23,44 |

Com essas medidas o tubo não encosta nos pinos de um bloco de baixo (sobram 0,18 mm). Quem segura são as 8 nervuras das paredes, alinhadas com os pinos: a ponta delas fica a 12,65 mm do centro (25,30 mm entre nervuras opostas), 0,03 mm para dentro do pino. Esse valor foi estimado, não medido no original, e o encaixe saiu bom com ele. As nervuras têm 1 mm de largura e um chanfro de entrada na base; os pinos, um chanfro de 0,4 mm no topo.

Imprimir com os pinos para cima, sem suporte. Para gerar com outra medida:

```bash
python3 duplo_2x2/make_duplo.py saida.stl rib_tip=12.7 stud_od=9.4
```

Parâmetros (mm): `half` (meia largura externa), `body_h`, `top_t` (laje do topo), `wall`, `tube_od`, `tube_id`, `stud_od`, `stud_id`, `stud_top` (altura do topo do pino), `stud_floor` (fundo do furo do pino), `stud_chamfer`, `pitch`, `rib_tip` (ponta da nervura, do centro), `rib_w`, `rib_leadin`, `rib_leadin_h`, `seg` (segmentos dos círculos), `overlap`. O STL é feito de cascas fechadas sobrepostas (laje, paredes, tubo, nervuras, pinos), que o Orca une ao fatiar.
