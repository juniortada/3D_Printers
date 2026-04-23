---
name: Graber i3 - Contexto e Plano de Fix MOSFET
description: Hardware da impressora, problema MOSFET D10 com defeito causando mesa aquecer ao ligar bico, e plano de fix redirecionando HEATER_0 para D9
type: project
---

## Hardware

- Impressora: Graber i3 (cartesiana)
- Placa: RAMPS 1.4 + Arduino Mega 2560
- Firmware: Marlin 2.1.2.5 (em `/home/junior/Documentos/printer/Graber/Marlin-2.1.2.5/`)
- Extrusor: Dragon (adaptador Graber), driver A4988, single hotend
- Mesa: MK2 heated bed
- Probe: BLTouch + AUTO_BED_LEVELING_BILINEAR
- `MOTHERBOARD = BOARD_RAMPS_14_EFB`

## Mapeamento de pinos (EFB atual)

- D10 = HEATER_0_PIN (bico) — **MOSFET DEFEITUOSO**
- D9  = FAN0_PIN (ventoinha)
- D8  = HEATER_BED_PIN (mesa)

## Problema

MOSFET do D10 com defeito: ao ligar o bico, corrente parasita ativa D8 (mesa),
causando aquecimento não solicitado e desigual da mesa (mais forte na traseira direita).

## Plano de fix (aguardando implementação — 2026-04-12)

Trocar D10 ↔ D9 via build flags no `platformio.ini`:

```ini
build_flags =
  ${common.build_flags}
  -DMOSFET_A_PIN=9
  -DMOSFET_B_PIN=10
```

Fisicamente: mover resistência do bico de D10 para D9; mover ventoinha de D9 para D10.
Mesa em D8 permanece inalterada. `Configuration.h` não precisa de alterações.

**Why:** MOSFET_A e B usam `#ifndef` em `pins_RAMPS.h` — build flags sobrescrevem antes.
**How to apply:** Qualquer sugestão de mudança de pino deve usar este método, não editar `Configuration.h` ou `pins_RAMPS.h` diretamente.

## Documentação completa

`/home/junior/Documentos/printer/Graber/CONTEXT_LLM.md`
