# How to print the model

Everything in this folder is already **sliced**: converted into the printer's own instructions by
Bambu Studio, with layer heights, speeds, temperatures and colours all set. You don't need to
install anything on a university laptop. Each `.gcode.3mf` file is one print job.

## Step 0: ask the print technicians three things (one email)

1. **Which Bambu Lab model are the printers?** The name is on the front: X1C (X1 Carbon), P1S,
   P2S or A1. Use the matching folder here. For any other model, see option C.
2. **Do they have an AMS?** That's the box on top that holds 4 spools and swaps them
   automatically. You need one for the 4-colour site model. Everything else is single colour.
3. **Do students press print themselves, or do technicians run the jobs?** This decides between
   option A and option B below. Also ask what they charge (per gram, or free for coursework).

Suggested email:

> Hi, for my Sustainable Design project I have a 1:100 / 1:1000 architectural model to print in
> PLA on the Bambu printers (about 1 kg in total, 9 jobs). The files are already sliced. Which
> models do you have, is there an AMS, and should I bring sliced .gcode.3mf files on a USB/SD card
> or send you Bambu Studio project files?

## Option A: you press print (simplest)

1. Copy the folder for your printer (`X1C/`, `P1S/`, `P2S/` or `A1/`) onto the printer's card:
   - **X1C, P1S, A1:** microSD card (the printer has a slot).
   - **P2S:** USB stick.
2. Put the card in, then on the printer's screen go to **Files** (the SD-card icon), pick the file
   and press **Print**.
3. If the screen asks for **filament mapping**, match each colour to the AMS slot holding it (see
   the table below). For a single-colour job, just load that colour.
4. Use the **textured PEI build plate** (the gold/black textured one, which is the normal plate on
   these printers). If the lab only has a smooth plate, choose it when the printer asks; PLA is fine on either.

## Option B: technicians run the jobs

Send them the 4 files in `project/`. These are normal Bambu Studio projects. They open with every
plate already laid out, named and coloured. If their printer model differs, they choose it at the
top left, click **Slice all**, then **Print**.

## Option C: a different printer, or you want to change something

Open a file from `project/` in Bambu Studio:
- **Linux:** `flatpak install --user flathub com.bambulab.BambuStudio`, then open it from your app menu.
- **Windows (no installer needed):** download the `Bambu_Studio_win-...zip` from
  <https://github.com/bambulab/BambuStudio/releases>, unzip it and run `bambu-studio.exe`. It needs
  Microsoft's Visual C++ runtime and Edge WebView2. Most Windows 10/11 machines already have them.
  If it won't start on a locked-down laptop, use option B or a lab PC.

Then pick your printer at the top left, click **Slice all**, and use **Print** or
**Export plate sliced file**.

## The print jobs

Times and grams below are from Bambu Studio for the X1C. Other models are within about 10%;
see `slice_report.md`. Start with something short, such as the PV strips, to check the printer
and filament before committing to the long jobs.

| File | What | Colour (AMS slot) | Time | PLA |
|---|---|---|---|---|
| `site_model_1to1000_4colour` | Site, 230 mm square | green 1, light grey 2, dark green 3, orange 4 | 11.4 h | 306 g |
| `site_model_1to1000_single_colour` | Site, if no AMS (paint after) | any 1 | 6.5 h | 248 g |
| `building_1to100_plate1_...` | Ground floor + cycle hub | white 1 | 4.5 h | 205 g |
| `building_1to100_plate2_...` | First floor | white 1 | 4.0 h | 177 g |
| `building_1to100_plate3_...` | Main roof + cycle-hub roof | light grey 2 | 3.7 h | 195 g |
| `building_1to100_plate4_...` | PV strips | dark blue 3 | 0.9 h | 22 g |
| `building_1to100_plate5_...` | Green roof | green 4 | 0.3 h | 9 g |
| `furniture_trays_1to100_plate1-3_...` | 21 room furniture trays | light grey 1 | 6.9 h total | 98 g |

The whole model (4-colour site + building + furniture) comes to **about 1 kg of PLA, about 32 h
of printing and about GBP 20** at GBP 20/kg. Choose only one of the two site versions.

The `plates/` folder has a picture of every job as it sits on the bed. The same picture appears on
the printer's screen and in Bambu Studio.

## After printing

- Peel parts off once the plate has cooled. Flexing the plate helps.
- **PV strips:** glue into the three pockets on the roof's south slopes with superglue or PVA.
  The engraved panel grid faces up.
- **Green roof:** glue on top of the cycle-hub roof.
- **Stacking:** ground floor, then first floor (pegs locate it), then roof. The cycle hub sits
  against the east end. The furniture trays drop into their rooms.
- **If the pegs are too tight,** sand them lightly. For a reprint, increase `HOLE_CLEARANCE_MM` in
  `src/config.py`, then run `python src/build_all.py` and `python src/bambu.py`.
