# Voron 2.4 — Klipper na MKS Monster8 V2 + Mainsail (Raspberry Pi)

Migração do firmware **Marlin 2.1.2.5** desta máquina para **Klipper** (no MCU) +
**Moonraker/Mainsail** (host no Raspberry Pi). Os parâmetros reais foram extraídos da
config Marlin desta impressora; a base é a config oficial da MKS
([makerbase-mks/MKS-Monster8](https://github.com/makerbase-mks/MKS-Monster8/tree/main/klipper%20firmware)),
com os valores reais sobrepostos.

> **Backup:** o Marlin original continua em `../Marlin/` (incl. `mks_monster8.bin`) para rollback.

## Hardware

| Item | Valor |
|---|---|
| Impressora | Voron 2.4, CoreXY, 305 × 305 × 300 mm |
| Placa | MKS Monster8 V2 — MCU **STM32F407VGT6** (1 MB flash) |
| Drivers | TMC2209 (UART) em X/Y/Z + 3× Z; **extrusor em A4988** (jumpers 16×) |
| Probe | BLTouch (sinal PB13, servo PA8); offset `-44 / 1.1 / 2.0` |
| Nivelamento | 4 motores Z → `quad_gantry_level` |
| Sensores | hotend ATC Semitec 104GT-2 (PC1) · mesa EPCOS 100K (PC0) · câmara EPCOS 100K (PC2) |
| Display | **MKS TS35 V2** (ST7796 480×320 + toque XPT2046) — ver seção do display |
| Comunicação | USB nativo (host ↔ MCU) |

## Estrutura dos arquivos

```
printer.cfg          # raiz: [mcu], [printer], board_pins e os includes
steppers.cfg         # X/Y + 4× Z (CoreXY, quad gantry)
tmc.cfg              # TMC2209 UART (extrusor A4988 NAO tem secao TMC)
extruder.cfg         # A4988, sensor Semitec, PID, pressure_advance
bed.cfg              # mesa EPCOS, PID
probe_leveling.cfg   # bltouch + safe_z_home + quad_gantry_level + bed_mesh
fans.cfg             # cooling, ventoinha de camara, (hotend fan comentado)
macros.cfg           # G32, PRINT_START, PRINT_END, CANCEL_PRINT
mainsail.cfg         # virtual_sdcard, pause_resume, exclude_object, PAUSE/RESUME
reference/           # configs oficiais MKS (generic + Voron 2.4 v1/v2) p/ diff
```

---

## 1. Compilar e gravar o firmware Klipper no MKS Monster8 V2

No Raspberry (após instalar o Klipper — ver passo 2):

```bash
cd ~/klipper
make menuconfig
```
Opções (conforme README/Image oficial da MKS):
- **Micro-controller Architecture:** STMicroelectronics STM32
- **Processor model:** STM32F407
- **Bootloader offset:** **48KiB bootloader**  ← equivale ao offset 0xC000 que o Marlin usa
- **Communication interface:** **USB (on PA11/PA12)**
- (clock: cristal de 8 MHz — padrão)

```bash
make
```

### Gravar
O `make flash` **não** funciona nesta placa. Copie o `.bin` para um microSD (FAT32) e resete:

```bash
cp ~/klipper/out/klipper.bin /caminho/sdcard/mks_monster8.bin
```
- Nome do arquivo: use **`mks_monster8.bin`** (é o que o comentário do config oficial do Klipper
  e o bootloader desta placa esperam — o mesmo nome que o Marlin já gravava).
  O README da MKS cita `firmware.bin`; se `mks_monster8.bin` não gravar, tente `firmware.bin`.
- Insira o SD na Monster8 e **resete a placa**. O bootloader grava e renomeia para `.CUR`.

### Alternativa: firmware pré-compilado
O repo MKS traz `mks_monster8 v0.10.0-557.bin`. Funciona como atalho, mas a versão do **host**
Klipper precisa ser compatível com a do MCU — **compilar você mesmo é mais seguro**.

### Conferir
Com o cabo USB ligado entre a placa e o Pi:
```bash
ls /dev/serial/by-id/*
```
Copie o caminho `usb-Klipper_stm32f407xx_...-if00` e cole em `[mcu] serial:` no `printer.cfg`.

---

## 2. Host: MainsailOS no Raspberry Pi

> **Atenção (Pi 2):** o Raspberry Pi 2 é ARMv7, 1 GB, sem Wi-Fi. Use a **imagem MainsailOS 32-bit**
> e rede **Ethernet** (ou dongle USB Wi-Fi). Roda Klipper/Moonraker/Mainsail, porém **lento** —
> input shaping e a UI web ficam pesados, mas o uso básico funciona. (Um Pi 3/4/Zero 2W é bem melhor.)

1. Grave o **MainsailOS** com o Raspberry Pi Imager; nas configurações avançadas defina hostname,
   usuário, SSH e rede.
2. Acesse por SSH, confirme que `klipper`, `moonraker` e `mainsail` estão ativos
   (MainsailOS já vem com tudo; senão use o **KIAUH**).
3. Coloque os arquivos desta pasta em `~/printer_data/config/` (veja a nota de integração abaixo).
4. Edite `[mcu] serial:` com o ID do passo 1 e dê `FIRMWARE_RESTART`.

### Integração com o Mainsail
Este conjunto é **autocontido**. Se o `printer.cfg` do MainsailOS já tiver `[include mainsail.cfg]`
apontando para o arquivo do **pacote**, **remova esse include** (o nosso `mainsail.cfg` já fornece
`virtual_sdcard`, `pause_resume`, `display_status`, `exclude_object` e `PAUSE`/`RESUME`) para
não duplicar seções. Versione esta pasta no git e crie um symlink/cópia para `~/printer_data/config/`.

---

## 3. Reaproveitar o display MKS TS35 V2 (experimental)

O Klipper **não dirige TFT colorido** pelos headers EXP1/EXP2 (a seção `[display]` só suporta
LCDs de caractere e gráficos mono 128×64). O TS35 V2 é um painel **ST7796 (480×320) + toque
resistivo XPT2046**, ambos em SPI. Como esses chips têm driver no Linux, o caminho para reaproveitar
é **religar o painel ao Raspberry Pi** e rodar **KlipperScreen** via framebuffer.

> Enquanto o display não estiver pronto, **controle tudo pelo Mainsail (navegador)** — a impressora
> funciona 100% sem o TS35.

### 3.1 Fiação TS35 (EXP1/EXP2) → GPIO do Raspberry Pi (3,3 V)
| Sinal do painel | Origem no EXP | Pino no Pi (BCM) |
|---|---|---|
| SCK  | EXP2_2 (PA5) | GPIO11 / SCLK (SPI0) |
| MOSI | EXP2_6 (PA7) | GPIO10 / MOSI |
| MISO | EXP2_1 (PA6) | GPIO9 / MISO |
| TFT_CS | EXP1_7 (PE15) | GPIO8 / CE0 |
| TOUCH_CS | EXP1_5 (PD9) | GPIO7 / CE1 |
| TFT_DC/RS | EXP1_8 (PE7) | um GPIO livre (ex.: GPIO24) |
| TFT_RESET | EXP1_4 (PD10) | um GPIO livre (ex.: GPIO25) |
| TFT_BL (backlight) | EXP1_3 (PE11) | 3,3 V (ou GPIO p/ PWM) |
| TOUCH PENIRQ | (verificar no cabo) | um GPIO livre (ex.: GPIO17) |
| 3V3 / GND | EXP_10 / EXP_9 | 3V3 / GND |

> Os pinos `PA5/PA7/PA6/PE15/...` acima são onde esses sinais saem **na placa** (referência
> `[board_pins]`); ao religar ao Pi o que importa é a função (SCK/MOSI/MISO/CS/DC/RST/BL/IRQ).
> Confirme o pinout impresso no próprio TS35. Se o cabo **não** expuser o **PENIRQ**, use o
> `ads7846` em modo *polled* com `pendown-gpio`.

### 3.2 Framebuffer (fbtft) + toque (ads7846)
Habilite SPI (`raspi-config` → Interface → SPI) e configure um overlay para **ST7796**
(480×320) e o **ads7846**/XPT2046. Em geral via `fbtft`/`flexfb` (pode exigir `fbtft-dkms`
e uma sequência de init custom do ST7796S). Ajuste rotação para *landscape* e calibre o toque.
O display aparece como `/dev/fb1`.

### 3.3 KlipperScreen
Instale o **KlipperScreen** e aponte-o para o `/dev/fb1` (X/framebuffer). 

> **Riscos/realidade:** desempenho do ST7796 por SPI/fbtft num **Pi 2** é baixo (poucos fps);
> a sequência de init do ST7796 pode dar trabalho. **Fallback:** usar só o Mainsail (web) ou um
> display **DSI/HDMI** conhecido para o KlipperScreen.

---

## 4. Primeira partida e calibração

Sempre confira **direção dos eixos** antes de qualquer movimento longo.

1. `FIRMWARE_RESTART` → `[mcu]` deve conectar sem erro.
2. **Endstops:** `QUERY_ENDSTOPS`. Movimente X/Y manualmente e confira CoreXY. Se um eixo for ao
   contrário, inverta o `dir_pin` no `steppers.cfg`. Se o homing bater longe do switch, inverta o
   `endstop_pin` (`!`).
3. **Homing:** `G28` (X/Y nos endstops max; Z via BLTouch no centro). Teste deploy/stow:
   `BLTOUCH_DEBUG COMMAND=pin_down` / `pin_up`.
4. **Quad gantry:** `QUAD_GANTRY_LEVEL` deve convergir (ajuste `gantry_corners` se necessário).
5. **PID:**
   ```
   PID_CALIBRATE HEATER=extruder TARGET=240
   PID_CALIBRATE HEATER=heater_bed TARGET=100
   SAVE_CONFIG
   ```
6. **Z-offset do BLTouch:** `PROBE_CALIBRATE` → ajuste com papel → `ACCEPT` → `SAVE_CONFIG`.
7. **Malha:** `BED_MESH_CALIBRATE` → `SAVE_CONFIG`.
8. **Extrusor (rotation_distance):** aqueça, marque 120 mm de filamento, `G1 E100 F60`, meça o
   consumido e corrija `rotation_distance` em `extruder.cfg`.
9. **Pressure advance:** calibre com `TUNING_TOWER` (método Klipper) e ajuste `pressure_advance`.
10. *(Opcional)* **Input shaper:** requer acelerômetro ADXL345 — recomendado para sustentar
    `max_accel: 5000`. Sem ADXL, mantenha os valores atuais (comprovados no Marlin).

### Velocidades — Marlin vs MKS vs adotado
| Parâmetro | Marlin | MKS v1 / v2 | **Adotado (mais rápido)** |
|---|---|---|---|
| max_velocity | 350 | 300 / 150 | **350** |
| max_accel | 5000 | 2000 / 2000 | **5000** |
| max_z_velocity | 15 | 15 / 15 | **15** |
| max_z_accel | 100 | 300 / 30 | **300** |
| cantos | JD 0.013 | scv 5.0 | **scv 5.0** |

---

## 5. Rollback para o Marlin
Copie `../Marlin/mks_monster8.bin` para o microSD e resete a placa. A impressora volta ao Marlin.

## Referências
- MKS Monster8 Klipper: <https://github.com/makerbase-mks/MKS-Monster8/tree/main/klipper%20firmware>
- Klipper Config Reference: <https://www.klipper3d.org/Config_Reference.html>
- Voron 2.4: <https://docs.vorondesign.com/build/software/>
- KlipperScreen: <https://klipperscreen.readthedocs.io/>
