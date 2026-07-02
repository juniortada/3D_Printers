# Voron 2.4 — Contexto para IA

Este arquivo descreve o hardware, firmware e configurações da impressora Voron 2.4 para uso em conversas com IA sem necessidade de reexplicar o contexto.

## Hardware

| Componente       | Especificação                    |
|------------------|----------------------------------|
| Impressora       | Voron 2.4                        |
| Área de impressão| 300 x 300 mm                     |
| Placa mãe        | MKS Monster 8 v2                 |
| Drivers          | TMC 2209 (X, Y, 4×Z), UART 3.3V — extrusores em A4988 |
| Ferramentas      | **2 toolheads** — Tapchanger/OptoTap + docks StealthChanger (adaptador Dragonburner) |
| Homing           | X **sensorless** (StallGuard TMC2209) · Y endstop físico · Z **OptoTap** por ferramenta |
| Extrusores       | 2× Voron M4 (Mobius) bowden, idênticos — A4988 nos slots E0 e E4 |
| Hotend           | Bambu (um por ferramenta)        |
| Nivelamento      | QGL + bed_mesh via OptoTap da ferramenta ativa (T0 de referência) |
| Fonte            | **24V** — Lumanti Slim 400W / 16,6A (mesa aquecida em AC via SSR, fora da fonte) |

## Firmware

- **Klipper** (firmware ativo) — configs em `Firmware/Klipper/` (`printer.cfg` + includes:
  `steppers.cfg`, `tmc.cfg`, `extruder.cfg`, `toolchanger.cfg`, `homing.cfg`, `fans.cfg`, etc.).
  MCU compilado para STM32F407 (bootloader 48KiB, USB) e gravado via SD (`mks_monster8.bin`).
- **Marlin 2** (legado) — em `Firmware/Marlin/`. As notas de Marlin abaixo são históricas.

## Slicer

- **Orca Slicer**
- Perfil de temperatura, retração e demais parâmetros configurados no Orca Slicer

## G-code Inicial (Start G-code)

```gcode
G90 ; use absolute coordinates
M83 ; extruder relative mode
M204 S[machine_max_acceleration_extruding] T[machine_max_acceleration_retracting]
M104 S[first_layer_temperature] ; set extruder temp
M140 S[first_layer_bed_temperature] ; set bed temp
G29 ; auto bed leveling (BL Touch)
G1 X30 Y30 F4000
G1 Z0 F100
M190 S[first_layer_bed_temperature] ; wait for bed temp
M109 S[first_layer_temperature] ; wait for extruder temp
G92 E0.0
; initial load
```

As variáveis entre `[]` são substituídas automaticamente pelo Orca Slicer.

## Notas de Configuração

- **Fonte 24V** (Lumanti Slim 400W / 16,6A): a máquina roda em 24V. A nota antiga de 12V
  (`CHOPPER_DEFAULT_12V`) valia só para o Marlin 12V legado — no Klipper isso não se aplica.
  Mesa aquecida é **AC via SSR** (não pesa na fonte 24V).
- **Mapeamento de drivers (MKS Monster8 v2)**:
  - Driver 0: X | Driver 1: Y
  - Driver 2-1: Z motor Front-Left (Marlin `Z`)
  - Driver 3: Extrusor A4988 (Marlin `E0`) — fica nos pinos E0, NÃO conflita com Z2
  - Driver 4: Z motor Rear-Left (Marlin `Z2`, usa pinos E1)
  - Driver 5: Z motor Rear-Right (Marlin `Z3`, usa pinos E2)
  - Driver 6: Z motor Front-Right (Marlin `Z4`, usa pinos E3)
  - Marlin pula o E0 ao alocar Z2/Z3/Z4 porque `E_STEPPERS=1`
- **Sensorless homing**: sensibilidade dos drivers TMC 2209 ajustada em `Configuration_adv.h` via `X_STALL_SENSITIVITY` e `Y_STALL_SENSITIVITY`
- **BL Touch**: configurado como probe Z; G29 executa o mesh antes de iniciar a impressão
- **Bowden**: comprimento do tubo e configurações de retração são críticos — ajustar no Orca Slicer e em `Configuration_adv.h`
- **MKS Monster 8 v2**: flash via cartão SD com arquivo `.bin` renomeado conforme documentação da placa

## Arquivos Relevantes

- [`Firmware/Marlin/Configuration.h`](Firmware/Marlin/Configuration.h)
- [`Firmware/Marlin/Configuration_adv.h`](Firmware/Marlin/Configuration_adv.h)
