# Kossel Mini — Marlin 2.1.2.7

Firmware configurado para a impressora delta Kossel Mini com placa AVR e BLTouch.

## Hardware

| Componente | Especificação |
|---|---|
| Placa | AVR (Arduino Mega / RAMPS) |
| Tipo | Delta (3 torres) |
| Probe | BLTouch |
| Raio imprimível | 110mm (diâmetro 220mm) |
| Haste diagonal | 235.5mm |

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
#define DELTA_HEIGHT           223.65   // calibrado com G33
#define DELTA_RADIUS           118.92   // calibrado com G33
#define DELTA_ENDSTOP_ADJ      { 0.0, -3.08, -3.37 }   // calibrado com G33
#define DELTA_TOWER_ANGLE_TRIM { -1.80, +0.01, +1.79 } // calibrado com G33
```

`DELTA_HEIGHT` é o valor mais crítico: define quantos mm o bico está acima da cama quando os carrinhos estão nos endstops. Se estiver muito baixo, o probe não alcança a cama durante o G33.

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
#define PROBING_MARGIN 15   // raio efetivo = DELTA_PRINTABLE_RADIUS - 15 = 95mm
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

1. Compilar e fazer upload do firmware
2. `G28` — verificar se os três carrinhos sobem corretamente
3. `G33` — calibração da geometria delta
4. `M500` — salvar na EEPROM
5. Atualizar `Configuration.h` com os valores do G33
6. Ajustar Z offset do BLTouch via M851
7. `G29` — nivelamento da cama (mesh)
8. `M500` — salvar mesh na EEPROM
