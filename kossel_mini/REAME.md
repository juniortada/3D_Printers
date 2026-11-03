# Kossel Mini — Marlin 2.1.2.9 + Dragon Burner

Firmware configurado para a impressora delta Kossel Mini com placa AVR, BLTouch e toolhead Dragon Burner ([kossel-dragon-burner](https://github.com/juniortada/kossel-dragon-burner), versão `left`).

Base: exemplo oficial `config/examples/delta/kossel_mini/Configuration.h` do Marlin Configurations release-2.1.2.7 (idêntico ao release-2.1.2.9), adaptado ao hardware desta máquina.

## Hardware

| Componente | Especificação |
|---|---|
| Placa | RAMPS 1.4 (Arduino Mega 2560) — `BOARD_RAMPS_14_EFB` |
| Tipo | Delta (3 torres, endstops MAX no topo) |
| Toolhead | Dragon Burner (V0.2 v8) com carenagem BLTouch `left`, bowden, V6 |
| Probe | BLTouch, à esquerda do bico (X −33,24 / Y −10,88), dispara com o bico 3,9 mm acima da mesa |
| Mesa | 3 parafusos com mola (entre as torres, cada um mais perto de X, Y e Z), PEI magnético |
| Área de impressão | **Ø210mm** (raio 105), menos as zonas perto das torres — ver [slicers](slicers/README.md) |
| Haste diagonal | 235.5mm |
| Drivers X/Y/Z | DRV8825 com 3 jumpers (1/32 microsteps → 160 steps/mm) |
| Driver E0 | A4988 |
| Termistores | Hotend e cama: 100k genérico (`TEMP_SENSOR_0=1`, `TEMP_SENSOR_BED=1`) |

---

## Calibração atual (2026-11-02, Marlin 2.1.2.9, Dragon Burner)

| Define | Valor | Origem |
|---|---|---|
| `DELTA_PRINTABLE_RADIUS` / `DELTA_MAX_RADIUS` | **105** | Ø210. O firmware **não** protege as torres: quem evita as zonas perto delas é o fatiador (ver abaixo) |
| `PROBING_MARGIN` | **5** | Anel do G33 em 65mm (105 − 5 − 35), probe até r=100 na mesa |
| `EXTRAPOLATE_BEYOND_GRID` | ativado | O probe não alcança X>40 (fica à esquerda do bico); fora da grade o mesh continua a inclinação em vez de achatar |
| `DELTA_HEIGHT` | **140.68** | G33 V3 |
| `DELTA_RADIUS` | **113.84** | G33 V3 |
| `DELTA_ENDSTOP_ADJ` | **{ -0.13, 0.00, -0.04 }** | G33 V3 (mesa nivelada) |
| `DELTA_TOWER_ANGLE_TRIM` | **{ -0.01, 0.08, -0.07 }** | G33 V3 |
| `NOZZLE_TO_PROBE_OFFSET` | **{ -33.24, -10.88, -3.90 }** | XY das STLs do projeto; Z pelo teste do cartão (~0,3mm) |
| `DEFAULT_KP` / `KI` / `KD` | **25.70 / 2.83 / 58.42** | `M303 E0 S220 C8` com a ventoinha de peça desligada |
| `DEFAULT_MAX_ACCELERATION` | { 2000, 2000, 2000, 500 } | Toolhead mais pesado; E500 era o valor da EEPROM |
| `DEFAULT_ACCELERATION` / `RETRACT` / `TRAVEL` | 700 / 5000 / 2000 | P e R da EEPROM antiga; travel reduzido pelo peso |
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

**Métricas de qualidade:**
- G33 V3 (4 pontos, anel de 65mm): stddev **0.017–0.022 mm**
- M48 (10 toques) no centro e na frente-direita: stddev **0.015 mm**
- Homing: 4 ciclos `G28` + sondagem perto de cada torre, variação ≤ **0.06 mm**
- Mesa plana: 8 pontos a no máximo **0.07 mm** de um plano
- Mesh salva (`G29 L-80 R70 F-90 B80`, frio): de **-0.19 a +0.18 mm**; os extremos são cantos extrapolados (fora do alcance do probe)

Backup da EEPROM antes da troca: `eeprom_backup_2026-11-02_marlin-2.1.2.7.txt`.

### Por que o centro e as bordas não batiam (calibração antiga)

A mesa estava inclinada em relação às torres e o G33 compensava isso com os endstops (`M666 {0, -3.49, -5.61}`). Numa delta, endstop desloca um carro inteiro; isso **curva** o caminho do bico em vez de incliná-lo. Com aqueles valores, o caminho do bico se afastava de um plano em 0,5mm até r=85 e 0,9mm até r=100. O G33 deixava plano só o anel que ele sonda; o mesh corrigia dentro da grade, mas fora dela o Marlin mantinha a altura da borda.

Correção: nivelar a mesa pelos parafusos até o G33 devolver `M666` perto de zero. Os carros estão iguais no topo (449mm da base do perfil nas três torres), então endstop grande sempre indica mesa inclinada.

### Renivelar a mesa

Quando o G33 devolver algum endstop acima de ~0,3mm:

```
M666 X0 Y0 Z0
G28
G30 X0 Y0
G30 X-47.5 Y-82.3
G30 X-41.3 Y59.0
G30 X38.0 Y3.5
G30 X-90 Y-20
G30 X10 Y-70
G30 X-30 Y60
G30 X25 Y30
```

Ajustar um plano nesses pontos e levar os três cantos à mesma altura. O parafuso Y-Z está no aperto máximo: ele é a referência e os outros dois só podem ser **soltos** (sobem). Meta: inclinação < 0,15mm a cada 100mm. Depois: `G33 V3`, `M500`.

## Fatiador

Perfis do OrcaSlicer (impressora + processos 0.12 / 0.20 / 0.28), textura e modelo da mesa e instalação em [slicers/README.md](slicers/README.md).

Mesa no fatiador: **circular, Ø210mm, origem no centro, altura máxima 115mm**, com a textura `slicers/orcaslicer/kossel_dragon_burner_bed.svg` (210×210mm em escala real, zonas das torres em vermelho: X frente-esquerda, Y frente-direita, Z trás). As zonas são só visuais: o fatiador não impede peças nelas.

Nada pode sair de r=105: quando um movimento sai do círculo, o Marlin encolhe o vetor inteiro, **inclusive o Z** (`motion.cpp`, `apply_motion_limits`), e o bico desceria sobre a peça.

```gcode
G28
M190 S{bed}                  ; mesa na temperatura
G33 O P1                     ; recalibra a altura com o probe no centro da mesa (~30s, faz o homing)
G29 L-80 R70 F-90 B80        ; mesh fresca (~2 min)
M109 S{hotend}
G92 E0
G1 X-40 Y-55 Z0.3 F3000      ; purga na frente, longe das torres
G1 X40 Y-55 E15 F1000
G92 E0
```

**Por que o `G33 O P1` a cada impressão:** em 2026-11-02 a altura medida no centro mudou ~0,9mm duas vezes sem causa identificada: às 20:08, entre dois homings, com tudo frio; e depois da calibração das 20:47, quando um `G33 O P1` às 22h mediu o centro 0,95mm mais baixo (`H` 140,68 → 141,63), com a mesa ainda a 47°C de um aquecimento anterior. Com a mesa já quente, ele recalcula o `H` antes do mesh e a primeira camada não sente essa variação. O `O` põe o probe no centro da mesa (o bico fica em X33 Y11, longe das torres). Ele só corrige certo se o que muda é a mesa ou a estrutura; se for o BLTouch se mexendo no suporte, o teste do papel no centro mostra a diferença.

Os limites `L-80 R70 F-90 B80` foram escolhidos para que todo ponto sondado deixe a cabeça a ≥10,5mm das torres: 18 pontos reais, cobrindo 79% da área segura. Não use outros limites sem refazer essa conta.

**G33 completo só re-rodar** quando trocar mecânica (correia, BLTouch, mesa, hastes).

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

### 5. Geometria da delta — valores do G33

```cpp
#define DELTA_PRINTABLE_RADIUS 105.0
#define DELTA_DIAGONAL_ROD     235.5
#define DELTA_HEIGHT           140.68
#define DELTA_RADIUS           113.84
#define DELTA_ENDSTOP_ADJ      { -0.13, 0.00, -0.04 }
#define DELTA_TOWER_ANGLE_TRIM { -0.01, 0.08, -0.07 }
```

`DELTA_HEIGHT` é o valor mais crítico. No Marlin 2.x ele é referenciado ao gatilho do probe: no homing o Z fica em `DELTA_HEIGHT - NOZZLE_TO_PROBE_OFFSET.z`. Depois de trocar o toolhead, **meça antes de mover**: `G28`, descer até Z=20 e conferir com a régua. Com a troca para o Dragon Burner, o valor antigo estava 35mm acima do real. O G33 desce até Z=50 para baixar o pino, o que teria batido o bico.

---

### 6. Calibração automática G33

```cpp
#define DELTA_AUTO_CALIBRATION
#define DELTA_CALIBRATION_DEFAULT_POINTS 4
```

Por padrão o G33 põe o **bico** no anel de sondagem e mede com o probe deslocado 35mm. Por isso os toques ficam perto da borda esquerda e longe da direita. Isso é esperado.

```
G28
G33 V3               ; ~15 min; conferir que M666 sai perto de zero
M500
```

Copiar os valores de `H`, `R`, endstop adj e tower angle trim do resultado do G33 para o `Configuration.h`.

---

### 7. Margem de probing

```cpp
#define PROBING_MARGIN 5
```

Numa delta o probe fica limitado a `DELTA_PRINTABLE_RADIUS - PROBING_MARGIN` do centro (r=100, dentro do PEI), e o anel do G33 é `DELTA_PRINTABLE_RADIUS - PROBING_MARGIN - |offset do probe|` = 65mm. Ao mudar o raio imprimível, ajustar a margem para manter o anel em 65mm, que é seguro em todas as direções. Numa delta a margem pode até ser negativa (o Marlin só a proíbe em cartesianas).

---

### 8. Z offset do BLTouch

```cpp
#define NOZZLE_TO_PROBE_OFFSET { -33.24, -10.88, -3.90 }
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

## Fluxo de configuração inicial

1. Compilar (`pio run -e mega2560`) e fazer upload (`pio run -e mega2560 -t upload`)
2. Conectar console serial em 115200 (Pronterface, OctoPrint ou `pio device monitor -b 115200`)
3. `M502` + `M500` + `M501` — reset da EEPROM com os defaults do `.h`
4. `G28` — verificar se os três carrinhos sobem em direção aos endstops MAX
5. `G1 Z20` no centro e conferir com a régua; corrigir com `M665 H` + `G28` antes de descer mais
6. `M401` / `M119` / `M402` / `M119` — BLTouch: `open` com o pino abaixado, `TRIGGERED` recolhido
7. Teste de folga: bico a Z=60 no limite de cada torre (X 74,5 / Y 83 / Z 92mm), conferindo a distância até a correia
8. `G28` + `G33 V3` — se `M666` vier acima de ~0,3mm, renivelar a mesa e repetir
9. `M500` — salvar na EEPROM
10. Ajuste do Z offset do BLTouch (seção 8) + `M500`
11. `M303 E0 S220 C8 U1` + `M500` — PID do hotend
12. `G28` + `G29 L-80 R70 F-90 B80` + `M500` — mesh salva
13. `M503` — copiar os valores para o `Configuration.h`

## Sincronização entre os dois caminhos

Após edições, manter sincronizado:

```bash
SRC=/home/junior/Documentos/upload/Marlin-2.1.2.9-kossel/Marlin
DST=/home/junior/Projetos/3D_Printers/kossel_mini
cp "$SRC/Configuration.h"     "$DST/Configuration.h"
cp "$SRC/Configuration_adv.h" "$DST/Configuration_adv.h"
```

| Caminho | Estrutura |
|---|---|
| `/home/junior/Documentos/upload/Marlin-2.1.2.9-kossel/` | árvore Marlin completa (compila daqui) |
| `/home/junior/Projetos/3D_Printers/kossel_mini/` | backup dos `.h`, `firmware-2.1.2.9-dragon-burner.hex` (o gravado em 2026-11-02) e os perfis de fatiador em `slicers/` |
