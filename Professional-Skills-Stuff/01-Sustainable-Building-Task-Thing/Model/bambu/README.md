# How to print the model

Everything in this folder is already **sliced**: converted into the printer's own instructions by
Bambu Studio, with layer heights, speeds, temperatures and colours all set. You don't need to
install anything on a university laptop. Each `.gcode.3mf` file is one print job.

## Which printer

The plan uses both of NTU's Bambu Lab printers. **Copy the contents of the card folder for the
campus you're going to onto a microSD card.** The files are already numbered in the order to print
them:

- **`sd_card_Clifton_RISE_X1E/`**: the 1:1000 site model, on the X1E (with AMS) in the RISE lab
  at Clifton.
- **`sd_card_City_X1C/`**: the 1:100 building and furniture, on the X1C in the 3D Printing Studio
  at City.

[`PRINT_PLAN.md`](PRINT_PLAN.md) explains the split and gives the timetable.

`X1C/` and `X1E/` hold the full set of jobs for each printer, in case plans change (for example,
the whole model on one printer). The model name is printed on the front of the printer. Use only
files made for that model, because each file is tagged with it.

None of NTU's other machines are needed: the Formlabs resin printers, the Markforged, the
Snapmaker and the SLS printer. The furniture prints fine on the Bambu printers.

## Step 0: ask the technicians two things (one email)

1. **Do students press print themselves, or do technicians run the jobs?** This decides between
   option A and option B below. Also ask how to book and what they charge (per gram, or free for
   coursework).
2. **Is the AMS loaded with your colours, or do you bring your own spools?** The AMS is the box
   that holds 4 spools and swaps them automatically. The RISE lab's X1E has one. You need it only
   for the 4-colour site model; everything else is single colour. Without an AMS, print the
   single-colour site instead and paint it.

Suggested email:

> Hi, for my Sustainable Design project I have a 1:100 / 1:1000 architectural model to print in
> PLA (about 1.1 kg in total). The files are already sliced, and every job finishes within a lab day.
> The 1:1000 site would be 3 jobs on the RISE X1E over two days (two of them use 4 colours in the
> AMS), and the 1:100 building would be 7 jobs on the City X1C over four days. Can I book time and
> run the jobs from a microSD card, or should I send you Bambu Studio project files? Do you supply
> PLA, and what does it cost?

## Option A: you press print (simplest)

**[`PRINT_PLAN.md`](PRINT_PLAN.md) has the timetable for both campuses (which job when, and why)
and a careful step-by-step checklist for launching each job.** In short:

1. Copy the contents of that campus's `sd_card_...` folder onto a **microSD card** (FAT32; most
   cards up to 32 GB already are). The slot is next to the printer's touchscreen. The X1E prints
   from the card even if the lab keeps it off the network.
2. Put the card in, then on the printer's screen go to **Files** (the SD-card icon), pick the file
   and press **Print**.
3. If the screen asks for **filament mapping**, match each colour to the AMS slot holding it (see
   the table below). For a single-colour job, just load that colour.
4. Use the **textured PEI build plate** (the gold/black textured one, which is the normal plate on
   these printers). If the lab only has a smooth plate, choose it when the printer asks; PLA is fine on either.

## Option B: technicians run the jobs

Send them the files in `project/`. These are normal Bambu Studio projects. They open with every
plate already laid out, named and coloured. If their printer model differs, they choose it at the
top left, click **Slice all**, then **Print**. To slice for a Bambu model other than the X1C or
X1E without the GUI, run `python src/bambu.py P1S` (P1S, P2S and A1 are set up).

## Option C: you want to change something

Open a file from `project/` in Bambu Studio:
- **Linux:** `flatpak install --user flathub com.bambulab.BambuStudio`, then open it from your app menu.
- **Windows (no installer needed):** download the `Bambu_Studio_win-...zip` from
  <https://github.com/bambulab/BambuStudio/releases>, unzip it and run `bambu-studio.exe`. It needs
  Microsoft's Visual C++ runtime and Edge WebView2. Most Windows 10/11 machines already have them.
  If it won't start on a locked-down laptop, use option B or a lab PC.

Then pick your printer at the top left, click **Slice all**, and use **Print** or
**Export plate sliced file**.

## The print jobs

Times and grams below are from Bambu Studio for the X1C. The X1E is within a few percent; see
`slice_report.md`. Start with something short, such as the PV strips, to check the printer
and filament before committing to the long jobs.

| File | What | Colour (AMS slot) | Time | PLA |
|---|---|---|---|---|
| `site_model_1to1000_4colour_halves_plate2_...` | Site, south half (the plan) | green 1, light grey 2, dark green 3, orange 4 | 5.6 h | 172 g |
| `site_model_1to1000_4colour_halves_plate1_...` | Site, north half (the plan) | as above | 6.8 h | 193 g |
| `site_model_1to1000_4colour` | Site in one piece, only if overnight printing is allowed | as above | 12.7 h | 350 g |
| `site_model_1to1000_single_colour` | Site in one piece, one colour (paint after) | any 1 | 6.6 h | 265 g |
| `building_1to100_plate1_...` | Ground floor + cycle hub | white 1 | 4.5 h | 205 g |
| `building_1to100_plate2_...` | First floor | white 1 | 4.0 h | 178 g |
| `building_1to100_plate3_...` | Main roof + cycle-hub roof | light grey 2 | 3.7 h | 195 g |
| `building_1to100_plate4_...` | PV strips | dark blue 3 | 0.9 h | 22 g |
| `building_1to100_plate5_...` | Green roof | green 4 | 0.3 h | 9 g |
| `furniture_trays_1to100_plate1-3_...` | 21 room furniture trays | light grey 1 | 6.9 h total | 98 g |

The whole model (4-colour site in two halves + building + furniture) comes to **about 1.1 kg of PLA,
about 33 h of printing and about GBP 21** at GBP 20/kg. Print the site only one way: halves,
one piece or one colour.

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
