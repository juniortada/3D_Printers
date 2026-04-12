# Voron 2.4 — Contexto para IA

Este arquivo descreve o hardware, firmware e configurações da impressora Voron 2.4 para uso em conversas com IA sem necessidade de reexplicar o contexto.

## Hardware

| Componente       | Especificação                    |
|------------------|----------------------------------|
| Impressora       | Voron 2.4                        |
| Área de impressão| 300 x 300 mm                     |
| Placa mãe        | MKS Monster 8 v2                 |
| Drivers          | TMC 2209 (X, Y, Z)               |
| Homing           | Sensorless (X, Y) via TMC 2209   |
| Extrusora        | Stealthburner com Bowden         |
| Hotend           | E3D V6                           |
| Nivelamento      | BL Touch (G29)                   |

## Firmware

- **Marlin 2**
- Arquivos em `Firmware/Marlin/`:
  - `Configuration.h` — configurações principais
  - `Configuration_adv.h` — configurações avançadas
  - `mks_monster8.bin` — binário compilado para a placa

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

- **Sensorless homing**: sensibilidade dos drivers TMC 2209 ajustada em `Configuration.h` via `X_STALL_SENSITIVITY` e `Y_STALL_SENSITIVITY`
- **BL Touch**: configurado como probe Z; G29 executa o mesh antes de iniciar a impressão
- **Bowden**: comprimento do tubo e configurações de retração são críticos — ajustar no Orca Slicer e em `Configuration_adv.h`
- **MKS Monster 8 v2**: flash via cartão SD com arquivo `.bin` renomeado conforme documentação da placa

## Arquivos Relevantes

- [`Firmware/Marlin/Configuration.h`](Firmware/Marlin/Configuration.h)
- [`Firmware/Marlin/Configuration_adv.h`](Firmware/Marlin/Configuration_adv.h)
