# Voron 2.4

> **Estado atual:** a máquina roda **Klipper** (configs em `Firmware/Klipper/`), fonte **24V**
> (Lumanti Slim 400W), com **2 toolheads** (Tapchanger/OptoTap + docks StealthChanger),
> hotend Bambu e 2× extrusor Voron M4 bowden. Homing: X sensorless, Y físico, Z por OptoTap.
> O conteúdo abaixo descreve o **build Marlin original** (legado, em `Firmware/Marlin/`).

## Hardware (build Marlin original — legado)

- Bed 300x300
- Board MKS Monster 8 v2
- Drivers TMC 2209 (X, Y, Z1, Z2, Z3, Z4)
- StealthBurner com Bowden
- Hotend E3D V6
- Firmware Marlin 2
- BL Touch (nivelamento Z)
- SensorLess Homing (X, Y)

---

## Domain Storytelling — Ciclo de Impressão

> Narrativa do fluxo completo: do arquivo 3D até a peça impressa.

```
[Usuário] fatia o modelo 3D com o [Orca Slicer]
    → gera o [G-code] com parâmetros de temperatura, velocidade e retração

[Orca Slicer] envia o [G-code] para o cartão SD ou via USB

[Usuário] inicia a impressão na [Impressora Voron 2.4]
    → [Marlin] executa o Start G-code:
        · aquece o hotend e a mesa
        · executa G28 (homing X/Y sensorless via TMC2209 StallGuard)
        · executa G29 (auto bed leveling via BL Touch, malha 3x3)
        · posiciona o bico em X30 Y30 para purga inicial

[Marlin] controla os [4 Motores Z] em sincronia via SpreadCycle
    → mantém o gantry nivelado durante toda a subida do eixo Z

[Marlin] aciona o [Stealthburner] para extrusão
    → deposita material camada por camada sobre a [Mesa 300x300]

[Impressora] conclui a impressão
    → [Marlin] executa End G-code (retração, desligamento, park)

[Usuário] retira a [Peça impressa] da mesa
```

---

## Compilar e Instalar o Firmware

### Pré-requisitos

- [Visual Studio Code](https://code.visualstudio.com/)
- Extensão [PlatformIO IDE](https://platformio.org/install/ide?install=vscode)
- Repositório do [Marlin](https://github.com/MarlinFirmware/Marlin) (versão compatível com os arquivos de configuração deste projeto)

### Passo a passo

**1. Preparar os arquivos de configuração**

Copie os arquivos deste repositório para dentro da pasta `Marlin/` do repositório Marlin:

```bash
cp Firmware/Marlin/Configuration.h    <marlin-repo>/Marlin/Configuration.h
cp Firmware/Marlin/Configuration_adv.h <marlin-repo>/Marlin/Configuration_adv.h
```

**2. Selecionar o environment da placa**

Abra o arquivo `platformio.ini` do repositório Marlin e confirme (ou ajuste) o environment:

```ini
[platformio]
default_envs = mks_monster8
```

A MKS Monster 8 v2 usa o environment `mks_monster8` (STM32F407).

**3. Compilar**

No VSCode com PlatformIO aberto:
- Clique em **PlatformIO: Build** (ícone ✓ na barra inferior), ou
- Use o terminal:

```bash
pio run -e mks_monster8
```

O binário gerado ficará em:
```
.pio/build/mks_monster8/firmware.bin
```

**4. Instalar na placa**

1. Renomeie o arquivo para `mks_monster8.bin` ou no meu caso funcionou com `firmware.bin` (a MKS Monster 8 v2 exige esse nome exato para o bootloader reconhecer)
2. Copie o `.bin` para a **raiz** de um cartão SD formatado em FAT32
3. Insira o cartão SD na impressora com ela **desligada**
4. Ligue a impressora — o LED da placa piscará durante o flash (~10 segundos)
5. Quando o LED parar de piscar e a tela inicializar, o firmware foi instalado com sucesso
6. Remova o cartão SD (o bootloader renomeia o arquivo após o flash; se não renomear, remova manualmente para evitar reflash a cada boot)

**5. Após o flash — configurações obrigatórias**

Execute via console (Pronterface, OctoPrint ou terminal serial):

```gcode
M502   ; carrega defaults do firmware
M500   ; salva na EEPROM
M503   ; confirma os valores gravados
```

> Sempre execute M502 + M500 após um novo flash para evitar conflito entre EEPROM antiga e novo firmware.

---

## Arquivos de Configuração

| Arquivo | Descrição |
|---------|-----------|
| [`Firmware/Marlin/Configuration.h`](Firmware/Marlin/Configuration.h) | Configurações principais (steps/mm, temperatura, homing, probe) |
| [`Firmware/Marlin/Configuration_adv.h`](Firmware/Marlin/Configuration_adv.h) | Configurações avançadas (Z auto-align, TMC drivers, hybrid threshold) |
| [`Firmware/Marlin/mks_monster8.bin`](Firmware/Marlin/mks_monster8.bin) | Último binário compilado |
| [`CLAUDE.md`](CLAUDE.md) | Contexto completo da máquina para uso com IA |
