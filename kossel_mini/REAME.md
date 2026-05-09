# Kossel Mini — Marlin 2.1.2.7

Firmware configurado para a impressora delta Kossel Mini com placa AVR e BLTouch.

Base: exemplo oficial `config/examples/delta/kossel_mini/Configuration.h` do Marlin Configurations release-2.1.2.7, adaptado ao hardware desta máquina.

## Hardware

| Componente | Especificação |
|---|---|
| Placa | RAMPS 1.4 (Arduino Mega 2560) — `BOARD_RAMPS_14_EFB` |
| Tipo | Delta (3 torres, endstops MAX no topo) |
| Probe | BLTouch |
| Raio imprimível | 110mm (diâmetro 220mm) |
| Haste diagonal | 235.5mm |
| Drivers X/Y/Z | DRV8825 com 3 jumpers (1/32 microsteps → 160 steps/mm) |
| Driver E0 | A4988 |
| Termistores | Hotend e cama: 100k genérico (`TEMP_SENSOR_0=1`, `TEMP_SENSOR_BED=1`) |

---

## Estado atual da calibração

A migração 2.1.2.6 → 2.1.2.7 zerou propositalmente as variáveis ajustáveis pelo G33 para uma recalibração limpa:

| Define | Valor atual | Pós-G33 |
|---|---|---|
| `DELTA_ENDSTOP_ADJ` | `{ 0.0, 0.0, 0.0 }` | a calibrar |
| `DELTA_TOWER_ANGLE_TRIM` | `{ 0.0, 0.0, 0.0 }` | a calibrar |
| `DELTA_HEIGHT` | `230.0` (estimativa alta) | a calibrar |
| `DELTA_RADIUS` | `120.0` (estimativa) | a calibrar |

Após executar G33 e M500, copiar os valores reais do `M503` para o `Configuration.h` e recompilar.

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
#define DELTA_PRINTABLE_RADIUS 110.0
#define DELTA_DIAGONAL_ROD     235.5
#define DELTA_HEIGHT           230.0   // estimativa alta — sobrescrito pelo G33
#define DELTA_RADIUS           120.0   // estimativa — sobrescrito pelo G33
#define DELTA_ENDSTOP_ADJ      { 0.0, 0.0, 0.0 }   // a calibrar com G33
#define DELTA_TOWER_ANGLE_TRIM { 0.0, 0.0, 0.0 }   // a calibrar com G33
```

`DELTA_HEIGHT` é o valor mais crítico: define quantos mm o bico está acima da cama quando os carrinhos estão nos endstops. **Começamos com 230.0 propositalmente alto** — assim o probe nunca bate na cama no primeiro G33. O G33 vai reduzir esse valor para o real.

---

### 6. Calibração automática G33

```cpp
#define DELTA_AUTO_CALIBRATION
#define DELTA_CALIBRATION_DEFAULT_POINTS 4
```

Habilita o comando G33. Procedimento inicial:

```
G28                  ; home nas torres
M665 H<estimativa>   ; ajuste preventivo se probe não alcançar a cama
G33                  ; calibração automática
M500                 ; salva na EEPROM
```

Copiar os valores de `H`, `R`, endstop adj e tower angle trim do resultado do G33 para o `Configuration.h`.

---

### 7. Margem de probing

```cpp
#define PROBING_MARGIN 10   // raio efetivo = DELTA_PRINTABLE_RADIUS - 10 = 100mm
```

Substitui o antigo `DELTA_CALIBRATION_RADIUS` (removido no Marlin 2.x). Define a margem de segurança entre a borda da área imprimível e os pontos de medição do G33 e G29.

---

### 8. Z offset do BLTouch

```cpp
#define NOZZLE_TO_PROBE_OFFSET { 23, 15, -2.00 }
```

Ajuste fino via M851 sem recompilar:

```
G28
G1 X0 Y0 Z10
; descer manualmente até o bico tocar a cama (teste do papel)
M851 Z<valor_negativo_anotado>
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
5. (Opcional) Ajuste manual grosso via `M666 X<n> Y<n> Z<n>` se uma torre estiver visivelmente fora
6. `M280 P0 S10` / `M280 P0 S90` — testar deploy/stow do BLTouch
7. `G28` + `G33 P4 V3` — calibração automática (repetir 1–2 vezes até stddev < 0,05mm)
8. `M500` — salvar na EEPROM
9. `M503` — anotar valores e copiar para o `Configuration.h` (DELTA_HEIGHT, DELTA_RADIUS, DELTA_ENDSTOP_ADJ, DELTA_TOWER_ANGLE_TRIM)
10. Ajuste fino do Z offset do BLTouch via `M851 Z<valor>` + `M500`
11. `G28` + `G29` — mesh bilinear da cama
12. `M500` — salvar mesh na EEPROM
13. Garantir `M420 S1` no start G-code do slicer para aplicar a mesh nos prints

## Sincronização entre os dois caminhos

Após edições, manter sincronizado:

```bash
SRC=/home/junior/Documentos/upload/Marlin-2.1.2.7-kossel/Marlin
DST=/home/junior/Projetos/3D_Printers/kossel_mini
cp "$SRC/Configuration.h"     "$DST/Configuration.h"
cp "$SRC/Configuration_adv.h" "$DST/Configuration_adv.h"
```

| Caminho | Estrutura |
|---|---|
| `/home/junior/Documentos/upload/Marlin-2.1.2.7-kossel/` | árvore Marlin completa (compila daqui) |
| `/home/junior/Projetos/3D_Printers/kossel_mini/` | apenas backup dos `.h` (raiz) |
