# Kossel Mini — Marlin 2.1.2.9 + Dragon Burner

Firmware configurado para a impressora delta Kossel Mini com placa AVR, BLTouch e toolhead Dragon Burner ([kossel-dragon-burner](https://github.com/juniortada/kossel-dragon-burner), versão `left`).

Base: exemplo oficial `config/examples/delta/kossel_mini/Configuration.h` do Marlin Configurations release-2.1.2.7 (idêntico ao release-2.1.2.9), adaptado ao hardware desta máquina.

## Hardware

| Componente | Especificação |
|---|---|
| Placa | RAMPS 1.4 (Arduino Mega 2560) — `BOARD_RAMPS_14_EFB` |
| Tipo | Delta (3 torres, endstops MAX no topo) |
| Toolhead | Dragon Burner (V0.2 v8) com carenagem BLTouch `left`, bowden, V6 |
| Probe | BLTouch, à esquerda do bico (X −33,24 / Y −10,88), dispara com o bico 3,3 mm acima da mesa |
| Mesa | Fixa, sem molas desde 2026-11-04: 3 parafusos apertados até o fim (entre as torres, cada um mais perto de X, Y e Z), PEI magnético |
| Área de impressão | **Ø210mm** (raio 105), menos as zonas perto das torres — ver [slicers](slicers/README.md) |
| Haste diagonal | 235.5mm |
| Carros | Guias lineares MGN9H com o carro de [`parts/carriage_mgn9h`](parts/carriage_mgn9h/README.md) (antes: patins de esferas) |
| Drivers X/Y/Z | DRV8825 com 3 jumpers (1/32 microsteps → 160 steps/mm) |
| Driver E0 | A4988 |
| Termistores | Hotend e cama: 100k genérico (`TEMP_SENSOR_0=1`, `TEMP_SENSOR_BED=1`) |

---

## Calibração atual (2026-11-04, Marlin 2.1.2.9, Dragon Burner)

| Define | Valor | Origem |
|---|---|---|
| `DELTA_PRINTABLE_RADIUS` / `DELTA_MAX_RADIUS` | **105** | Ø210. O firmware **não** protege as torres: quem evita as zonas perto delas é o fatiador (ver abaixo) |
| `PROBING_MARGIN` | **5** | Anel do G33 em 65mm (105 − 5 − 35), probe até r=100 na mesa |
| `EXTRAPOLATE_BEYOND_GRID` | ativado | Só conta se voltar a usar o `G29`: o probe não alcança X>40 (fica à esquerda do bico); fora da grade o mesh continua a inclinação em vez de achatar |
| `DELTA_HEIGHT` | **151.78** | Compensação da mesa fixa ([`calibration/bed_shift.py`](calibration/README.md#mesa-mudou-de-lugar-bed_shiftpy)); o `G33 O P1` refaz antes de cada impressão |
| `DELTA_RADIUS` | **113.15** | Peça de calibração do Klipper ([`calibration/klipper_fit.py`](calibration/README.md#ângulos-e-raio-peça-do-klipper)) |
| `DELTA_ENDSTOP_ADJ` | **{ 0.00, -1.86, -0.40 }** | Primeira camada (7 quadrados), mantida no ajuste dos ângulos e compensada para a mesa fixa |
| `DELTA_TOWER_ANGLE_TRIM` | **{ 1.19, 0.71, 0.01 }** | Peça de calibração do Klipper |
| `NOZZLE_TO_PROBE_OFFSET` | **{ -33.24, -10.88, -3.30 }** | XY das STLs do projeto; Z pela primeira camada |
| `DEFAULT_KP` / `KI` / `KD` | **25.70 / 2.83 / 58.42** | `M303 E0 S220 C8` com a ventoinha de peça desligada |
| `DEFAULT_MAX_ACCELERATION` | { 3000, 3000, 3000, 500 } | Guias MGN; 30 deslocamentos a 150mm/s com acel. 3000 mudaram o centro em no máximo 0,06mm (sem perda de passo). E500 era o valor da EEPROM |
| `DEFAULT_ACCELERATION` / `RETRACT` / `TRAVEL` | 1500 / 5000 / 3000 | Guias MGN (mesmo teste acima); R da EEPROM antiga |
| `DEFAULT_EJERK` | 1.5 | Valor da EEPROM antiga |

### Zonas proibidas perto das torres

O BLTouch encostou na correia da torre X com o bico em r≈90. As folgas medidas com o bico em r=75 (torre X 10mm, Y 18mm, Z 27mm) batem com as correias a ~128mm do centro nas três torres. Com a projeção da cabeça montada (STLs do projeto do Dragon Burner) e 10mm de folga, o bico pode avançar no máximo:

| Direção | Limite do bico (do centro) | Peça mais próxima da torre |
|---|---|---|
| Torre X (frente-esquerda) | **74,5mm** | carenagem do BLTouch (43mm além do bico) |
| Torre Y (frente-direita) | **83mm** | ventoinha 4010 (35mm além do bico) |
| Torre Z (trás) | **92mm** | effector (26mm além do bico) |
| Entre as torres | 105mm (borda de Ø210) | — |

Área segura: ~31.000mm², 1,75× a de um círculo de Ø150.

Como o firmware aceita qualquer ponto até r=105:
- **Não mover o bico perto das torres pelo LCD** (Move Axis) nem com G1 manual.
- Peças, saia, brim e purga fora das zonas vermelhas da textura da mesa (`slicers/`). O fatiador não bloqueia essas zonas.
- Calibração continua segura: anel do G33 a ≥19,9mm das torres; `G29 L-80 R70 F-90 B80` a ≥10,5mm; o "Level Bed" do LCD (grade padrão ±70) a ≥9,2mm. **Não aumentar `GRID_MAX_POINTS_X`**: com 7×7 a grade padrão encosta na torre Y.
- Os 7 pontos de `calibration/probe_7_points.gcode` foram conferidos com a cabeça montada: o da torre Y deixa o bico em r=104,6, a poucos mm da correia.

**Como está hoje:**
- Primeira camada: os 7 quadrados de [`calibration/first_layer_7_pads.gcode`](calibration/README.md#primeira-camada-7-quadrados), sem malha, saem todos bons.
- XY: o [Duplo 2x2](calibration/README.md#duplo-2x2) impresso encaixa macio num Duplo original. A peça do Klipper não foi reimpressa depois da correção.
- Probe: as 7 leituras de referência repetem a ±0,05mm. Com a mesa fixa, 5 rodadas em 16 min, a partir de 1 min com a mesa a 50 °C, variaram no máximo 0,10mm por ponto.
- Homing: 6 ciclos a ≤0,10mm (seção 10).

Backups da EEPROM: `eeprom_backup_2026-11-02_marlin-2.1.2.7.txt` (antes da troca de firmware) e `eeprom_backup_2026-11-04_mesa_fixa.txt` (a atual).

**O firmware gravado na impressora ainda tem os padrões de 2026-11-02.** A EEPROM tem os valores certos, mas um `M502` voltaria à geometria antiga. O `.hex` deste repositório já tem os padrões novos: grave-o antes de usar `M502`.

### Como esta calibração foi feita (2026-11-03 e 04)

Com os carros MGN9H instalados, a calibração recomeçou do zero:

1. **`G33` completo**, com o endstop Z acertado à mão (estava ~2mm mais baixo) e a mesa nos parafusos de mola apertados até o fim: desvio de 0,023mm, `M666 Y−3,29 Z−0,83`. Mas a peça de XY saiu com a frente esmagada e o pino do fundo sem grudar.
2. **Probe no ponto mais perto de cada torre** (r=80, em vez do anel de 65mm do G33): `M666 Y−1,92 Z−1,08`, `R 113,95`. A primeira camada continuou ruim com `G29` e melhorou muito sem ele: o `G29` estava piorando (seção 11 e item 6).
3. **Pelo bico, não pelo probe:** o cartão e os 7 quadrados mostraram o lado entre X e Z alto e o centro mais esmagado que as bordas (prato), o que o probe não via. Corrigido pelo bico: `M666 Y−1,37 Z−1,42`, `R 112,71`, `M851 Z −3,30`.
4. **Ângulos pela peça do Klipper:** ela saiu em losango, com ~0,7% de cisalhamento e Y 0,8% mais curto que X. O modelo da delta deu torre X +1,42°, torre Y +0,49° e raio +0,44mm, com o `M666` recalculado para a primeira camada não mudar. Aplicado, o probe mudou ponto a ponto como o modelo previa (até 0,11mm de diferença).
5. **Mesa sem molas:** com as molas, a leitura do probe chegou a mudar 1,4mm nos primeiros ~10 min depois de aquecer a mesa, e depois voltava sozinha. Sem as molas, a mesa desceu 8,0–8,9mm e inclinou; `H` e `M666` foram recalculados para o bico ficar na mesma relação com a mesa (`H 151,78`, `M666 Y−1,86 Z−0,40`). A leitura ficou estável desde o primeiro minuto.
6. **Sem malha:** mesmo com a geometria calibrada, o probe lê o fundo e o lado esquerdo 0,4–0,6mm acima do centro, e o bico não vê isso. A malha levantava o bico ali: na peça do Klipper, os pilares do fundo e o da torre Y ficaram longe da mesa.
7. **Conferência:** 7 quadrados perfeitos sem malha e um Duplo 2x2 encaixando num original.

O `M666` grande não indica mais mesa a nivelar: com a mesa fixa, é ele que acompanha a inclinação dela (~1mm a cada 100mm). Isso também curva um pouco o caminho do bico (até 0,16mm de um plano até r=85), e os quadrados saem bons assim.

### Por que não usar o G33 completo nem o G29

O BLTouch fica 35mm à esquerda do bico, e a diferença entre a altura que ele mede e a do bico muda com a posição na mesa (até 0,6mm entre o centro e o fundo-esquerdo). O `G33` completo e o `G29` nivelam pelo probe, então desfazem a calibração feita pelo bico:
- **`G33 P2` ou mais** (inclusive o `V3` e a calibração automática pelo LCD) sobrescreve `M666`, raio e ângulos. Se rodar por engano, `M501` recarrega a EEPROM; não dê `M500` antes.
- **`G29`** levanta o bico onde o probe lê alto. O gcode inicial do Orca usa `M420 S0`.
- **`G33 O P1`** só mede o centro e refaz o `H`, sem mexer no resto: esse continua no início de cada impressão.

Até 2026-11-02 a calibração era o `G33 V3`, com a mesa nivelada pelos parafusos de mola até o `M666` sair perto de zero.

### Recalibrar

Ferramentas e passo a passo em [`calibration/`](calibration/README.md):
- **Mesa tirada, calçada ou com outra altura:** sondar os 7 pontos de referência e recalcular `H` e `M666` (`bed_shift.py`).
- **Hastes, carros, torres ou correias trocados, ou peças em losango:** peça do Klipper (`klipper_fit.py`) e depois os 7 quadrados.
- **Primeira camada toda esmagada ou toda alta:** `M851 Z` (seção 8).

## Fatiador

Perfis do OrcaSlicer (impressora + processos 0.12 / 0.20 / 0.28 / Calibração), textura e modelo da mesa e instalação em [slicers/README.md](slicers/README.md).

Mesa no fatiador: **circular, Ø210mm, origem no centro, altura máxima 115mm**, com a textura `slicers/orcaslicer/kossel_dragon_burner_bed.svg` (210×210mm em escala real, zonas das torres em vermelho: X frente-esquerda, Y frente-direita, Z trás). As zonas são só visuais: o fatiador não impede peças nelas.

Nada pode sair de r=105: quando um movimento sai do círculo, o Marlin encolhe o vetor inteiro, **inclusive o Z** (`motion.cpp`, `apply_motion_limits`), e o bico desceria sobre a peça.

```gcode
G28
M190 S{bed}                  ; mesa na temperatura
G33 O P1                     ; recalibra a altura com o probe no centro da mesa (~13s, faz o homing)
M420 S0                      ; sem malha
M109 S{hotend}
G92 E0
G1 X-30 Y-80 Z0.3 F3000      ; purga na frente, fora de peças de até 140mm e longe das torres
G1 X30 Y-80 E12 F1000
G92 E0
```

**Por que o `G33 O P1` a cada impressão:** em 2026-11-02 a altura medida no centro mudou ~0,9mm duas vezes sem causa identificada, e em 2026-11-04 a leitura chegou a mudar 1,4mm nos primeiros ~10 min depois de aquecer a mesa. Nas duas vezes a mesa estava nas molas. Fixa, ela ficou estável desde o primeiro minuto a 50 °C, então o gcode não espera depois do `M190`. O `G33 O P1` fica porque leva ~13s e acerta a altura com a mesa já quente. O `O` põe o probe no centro da mesa (o bico fica em X33 Y11, longe das torres). Ele só corrige certo se o que muda é a mesa ou a estrutura; se for o BLTouch se mexendo no suporte, o teste do papel no centro mostra a diferença.

**Sem malha:** ver [Por que não usar o G33 completo nem o G29](#por-que-não-usar-o-g33-completo-nem-o-g29). Se voltar a usar o `G29`: os limites `L-80 R70 F-90 B80` foram escolhidos para que todo ponto sondado deixe a cabeça a ≥10,5mm das torres: 18 pontos reais, cobrindo 79% da área segura. Não use outros limites sem refazer essa conta.

**Não rodar o G33 completo.** Depois de trocar mecânica, recalibrar pelo [`calibration/`](calibration/README.md).

**Atenção:** com o pino recolhido, a ponta do BLTouch fica poucos mm acima do bico. Se começar a raspar nas peças, remodelar o suporte da carenagem para subir o BLTouch e refazer o `M851 Z`.

---

## Pontos principais de ajuste para delta

### 1. CLASSIC_JERK — obrigatório para delta

```cpp
#define CLASSIC_JERK
```

Impressoras delta e SCARA exigem `CLASSIC_JERK`. Sem ele, o Marlin não compila. O modo Junction Deviation não é compatível com a cinemática delta.

---

### 2. Limites de movimento (X/Y MIN e MAX)

```cpp
#define X_MIN_POS -(DELTA_PRINTABLE_RADIUS)
#define Y_MIN_POS -(DELTA_PRINTABLE_RADIUS)
#define X_MAX_POS  (DELTA_PRINTABLE_RADIUS)   // positivo
#define Y_MAX_POS  (DELTA_PRINTABLE_RADIUS)   // positivo
```

Em delta os limites MAX devem ser **positivos** (espelho dos MIN). Se ambos forem negativos, `X_MAX_LENGTH = 0` e a sanity check falha na compilação.

---

### 3. Direção dos motores

```cpp
#define INVERT_X_DIR true
#define INVERT_Y_DIR true
#define INVERT_Z_DIR true
```

Numa delta os carrinhos sobem em direção aos endstops (posição home = MAX). Se algum carrinho descer ao invés de subir no home, inverta o `INVERT_*_DIR` da torre correspondente **ou** inverta fisicamente o conector do motor no driver.

> **Atenção DRV8825:** o DRV8825 tem polaridade de DIR invertida em relação ao A4988. Após a primeira gravação, comande `G28` com a mão pronta no botão de reset; se um carro descer, inverta `INVERT_*_DIR` daquela torre para `false` (ou vire fisicamente o conector do motor).

---

### 4. Direção de homing — sempre para MAX

```cpp
#define X_HOME_DIR 1
#define Y_HOME_DIR 1
#define Z_HOME_DIR 1
```

Os endstops ficam no topo das torres. O home sempre sobe.

---

### 5. Geometria da delta

```cpp
#define DELTA_PRINTABLE_RADIUS 105.0
#define DELTA_DIAGONAL_ROD     235.5
#define DELTA_HEIGHT           151.78
#define DELTA_RADIUS           113.15
#define DELTA_ENDSTOP_ADJ      { 0.00, -1.86, -0.40 }
#define DELTA_TOWER_ANGLE_TRIM { 1.19, 0.71, 0.01 }
```

`DELTA_HEIGHT` é o valor mais crítico. No Marlin 2.x ele é referenciado ao gatilho do probe: no homing o Z fica em `DELTA_HEIGHT - NOZZLE_TO_PROBE_OFFSET.z`. Depois de trocar o toolhead, **meça antes de mover**: `G28`, descer até Z=20 e conferir com a régua. Com a troca para o Dragon Burner, o valor antigo estava 35mm acima do real. A sondagem desce rápido até Z=8,3 sem tocar na mesa (seção 10): com a altura errada, ela bateria o bico.

---

### 6. Calibração automática G33

```cpp
#define DELTA_AUTO_CALIBRATION
#define DELTA_CALIBRATION_DEFAULT_POINTS 4
```

O G33 fica ligado pelo `G33 O P1`, que mede só o centro com o probe (`O`) e refaz o `H` antes de cada impressão. O G33 completo não é usado: ver [Por que não usar o G33 completo nem o G29](#por-que-não-usar-o-g33-completo-nem-o-g29).

Por padrão o G33 põe o **bico** no anel de sondagem e mede com o probe deslocado 35mm. Por isso os toques ficam perto da borda esquerda e longe da direita. Isso é esperado.

---

### 7. Margem de probing

```cpp
#define PROBING_MARGIN 5
```

Numa delta o probe fica limitado a `DELTA_PRINTABLE_RADIUS - PROBING_MARGIN` do centro (r=100, dentro do PEI), e o anel do G33 é `DELTA_PRINTABLE_RADIUS - PROBING_MARGIN - |offset do probe|` = 65mm. Ao mudar o raio imprimível, ajustar a margem para manter o anel em 65mm, que é seguro em todas as direções. Numa delta a margem pode até ser negativa (o Marlin só a proíbe em cartesianas).

---

### 8. Z offset do BLTouch

```cpp
#define NOZZLE_TO_PROBE_OFFSET { -33.24, -10.88, -3.30 }
```

Ajuste fino via M851 sem recompilar. Como `DELTA_HEIGHT` é referenciado ao probe, mudar o `M851 Z` desloca o zero do bico direto, sem refazer o G33:

```
G28
G1 X0 Y0 Z3
; LCD: Motion > Move Axis > Move Z > 0.1mm, descer até o papel/cartão prender
; novo M851 Z = M851 Z atual + (Z onde prendeu - espessura do papel/cartão)
M851 Z<novo>
G28
M500
```

---

### 9. EEPROM

```cpp
#define EEPROM_SETTINGS
```

Necessário para que M500/M501 funcionem. Sem isso, os valores do G33 só sobrevivem até o próximo reset.

---

### 10. Velocidade da sondagem e do homing

```cpp
#define XY_PROBE_FEEDRATE (100*60)
#define Z_PROBE_FEEDRATE_FAST (50*60)
#define Z_PROBE_FEEDRATE_SLOW (5*60)
//#define MULTIPLE_PROBING 2
#define Z_CLEARANCE_DEPLOY_PROBE   10
#define Z_CLEARANCE_BETWEEN_PROBES  5
#define HOMING_FEEDRATE_MM_M { (60*60), (60*60), (60*60) }
```

Cada ponto é **um toque lento**. Com `MULTIPLE_PROBING 2` o Marlin devolve `(lento×3 + rápido×2)/5`, e o toque rápido entra na medida. Com um toque só, o rápido só aproxima o probe e não encosta na mesa.

**Patch no Marlin** (`Marlin/src/module/probe.cpp`, `run_z_probe`): a aproximação rápida para em `Z_CLEARANCE_BETWEEN_PROBES + |offset Z|` (8,3mm, com o gatilho do pino a 5mm da mesa), em vez de `Z_CLEARANCE_DEPLOY_PROBE + 5 + |offset Z|` (18,3mm). O toque lento fica com 5mm, cerca de 1s. Se a aproximação tocar a mesa antes, o Marlin sobe 5mm e mede devagar. O patch está em `marlin-probe-approach.patch`. Reaplicar ao trocar a versão do Marlin:

```bash
cd /home/junior/Documentos/upload/Marlin-2.1.2.9-kossel
patch -p1 < /home/junior/Projetos/3D_Printers/kossel_mini/marlin-probe-approach.patch
```

| | Antes (2026-11-02) | Agora |
|---|---|---|
| `G30` | 16s | 6s |
| `G33 O P1` | ~20s | ~13s |
| `G29 L-80 R70 F-90 B80` (18 pontos) | ~120s | 63s |
| Homing, 6 ciclos (centro) | ≤0,07mm | ≤0,10mm |

**Não acelerar o homing.** Com o homing a 100mm/s e recuo de 3mm, a posição de home saltou ~1mm entre um homing e outro. Esse salto equivale a uma torre errando 3mm, que é o recuo, como um switch que não soltou ao recuar. Os endstops ficam nos esticadores das correias. Com 60mm/s e recuo de 5/5/2mm (`HOMING_BUMP_MM` padrão), a variação volta para ≤0,1mm. Na mesma rodada o `XY_PROBE_FEEDRATE` estava em 150, e voltou para 100 junto com o homing: essa velocidade não foi testada sozinha.

**`BLTOUCH_HS_MODE` não foi ligado.** Ele economizaria ~1s por ponto do `G29`, mas acrescenta um campo na EEPROM, que voltaria aos padrões na gravação.

**Homing a 80mm/s também foi testado** (recuo 5/5/2mm, segundo toque a 27/16mm/s): a posição de home variou 0,29mm em 10 ciclos e o primeiro toque depois do homing saía 0,1–0,2mm alto. Fica em 60mm/s.

---

### 11. Cantos da grade do G29

Com `G29 L-80 R70 F-90 B80`, 7 dos 25 pontos da grade ficam fora do alcance do probe: (−80,−90), (70,−90), (70,−47,5), (70,37,5), (−80,80), (32,5,80) e (70,80). No Marlin original, numa delta, o `G29` copia a grade salva e só zera tudo quando os limites mudam. Esses 7 pontos eram preenchidos (extrapolados) só no primeiro `G29` e depois **nunca mais mudavam**: até 2026-11-04 eles vinham do mesh de 2026-11-02, ainda com os carros antigos. Comparados com o mesh de 2026-11-04, erravam até 0,73mm. Na impressão com `G29`, isso baixava o bico 0,24mm no pino fundo-direito da peça de XY e até 0,9mm na borda do fundo. Os pontos à esquerda e o centro não eram afetados.

**Patch** (`Marlin/src/gcode/bedlevel/abl/G29.cpp`, `marlin-g29-reset-grid.patch`): a grade é zerada a todo `G29`, e os 7 pontos são extrapolados da medição nova. Desde 2026-11-04 as impressões não usam o `G29` ([por quê](#por-que-não-usar-o-g33-completo-nem-o-g29)); o patch fica para quando ele for usado.

```bash
cd /home/junior/Documentos/upload/Marlin-2.1.2.9-kossel
patch -p1 < /home/junior/Projetos/3D_Printers/kossel_mini/marlin-g29-reset-grid.patch
```

---

## Fluxo de configuração inicial

1. Compilar (`pio run -e mega2560`) e fazer upload (`pio run -e mega2560 -t upload`)
2. Conectar console serial em 115200 (Pronterface, OctoPrint ou `pio device monitor -b 115200`)
3. `M502` + `M500` + `M501` — reset da EEPROM com os defaults do `.h`
4. `G28` — verificar se os três carrinhos sobem em direção aos endstops MAX
5. `G1 Z20` no centro e conferir com a régua; corrigir com `M665 H` + `G28` antes de descer mais
6. `M401` / `M119` / `M402` / `M119` — BLTouch: `open` com o pino abaixado, `TRIGGERED` recolhido
7. Teste de folga: bico a Z=60 no limite de cada torre (X 74,5 / Y 83 / Z 92mm), conferindo a distância até a correia
8. Primeira camada com os 7 quadrados (`calibration/first_layer_7_pads.gcode`); se a mesa mudou de lugar, recalcular `H` e `M666` pelo `calibration/` (seção [Recalibrar](#recalibrar))
9. `M500` — salvar na EEPROM
10. Ajuste do Z offset do BLTouch (seção 8) + `M500`
11. `M303 E0 S220 C8 U1` + `M500` — PID do hotend
12. `M503` — copiar os valores para o `Configuration.h` e salvar um backup da EEPROM

## Sincronização entre os dois caminhos

Após edições, manter sincronizado:

```bash
SRC=/home/junior/Documentos/upload/Marlin-2.1.2.9-kossel/Marlin
DST=/home/junior/Projetos/3D_Printers/kossel_mini
cp "$SRC/Configuration.h"     "$DST/Configuration.h"
cp "$SRC/Configuration_adv.h" "$DST/Configuration_adv.h"
```

Ao mudar o `probe.cpp` ou o `G29.cpp`, refazer o patch correspondente (seções 10 e 11).

| Caminho | Estrutura |
|---|---|
| `/home/junior/Documentos/upload/Marlin-2.1.2.9-kossel/` | árvore Marlin completa, com os patches do `probe.cpp` e do `G29.cpp` aplicados (compila daqui) |
| `/home/junior/Projetos/3D_Printers/kossel_mini/` | backup dos `.h`, `marlin-probe-approach.patch`, `marlin-g29-reset-grid.patch`, `firmware-2.1.2.9-dragon-burner.hex` (compilado deste `Configuration.h`), backups da EEPROM, as ferramentas de calibração em `calibration/` e os perfis de fatiador em `slicers/` |
