# Print plan: two campuses, one week, and how to launch a job

## Who prints what

| Where | Printer | Prints | Card folder | Printing time |
|---|---|---|---|---|
| **Clifton**, RISE laboratory | Bambu Lab **X1E** (has the AMS) | The 1:1000 site model in two halves, plus the small green roof as a test job | `sd_card_Clifton_RISE_X1E/` | about 11 h over 2 days |
| **City**, 3D Printing Studio | Bambu Lab **X1C** | The 1:100 building and its furniture | `sd_card_City_X1C/` | about 20 h over 4 days |

**Why this split:**
- **The site is the only job that needs 4 colours,** so it goes on the X1E, which has the AMS
  (the box that swaps between 4 spools). Every building and furniture job is single colour, so it
  doesn't matter whether the City X1C has an AMS.
- **The site is the most fragile piece.** It isn't big: it's a flat 229 x 229 mm square, 27 mm
  tall, about the size of a dinner plate. But its 1:1000 trees are tiny spikes that snap off.
  Printed at Clifton, it only travels across campus.
- **The building travels well.** It's 6 separate flat pieces, each no bigger than 240 x 156 mm
  and 38 mm tall, plus the furniture trays. Everything fits in a shoebox-sized box on the tram.
- **Both printers can run in the same week,** so everything is done in about 4 days, not 6.

Each card folder holds exactly the files for that printer, numbered in the order to print them.
The printer lists files alphabetically, so 01 is at the top. Copy the **contents** of the folder
onto that campus's microSD card.

## Clifton (RISE lab, X1E): two days

In one piece, the 4-colour site takes 11.5 hours, which means printing overnight. About 5 of
those hours are colour changes. The printer swaps colour around 190 times, at roughly 1.5
minutes each, and the swaps happen on almost every layer however small the model is. So the
site is printed as **two halves, each a separate job that fits in one lab day**.
- The cut runs east-west just south of the proposal. It misses the proposed building and every
  existing building, crossing only grass, paths and trees.
- The halves use slightly thicker layers (0.28 mm instead of 0.20 mm). At 1:1000 that makes the
  terrain read like contour steps, which suits an architectural model.

Try to book these **early in the week**, so a failed print still leaves time for another go.
Load the AMS first: **green, light grey, dark green, orange**.

| Day | Start | File on the card | Colour | Takes | Done by | Notes |
|---|---|---|---|---|---|---|
| **A** | 09:30 | `01_building_..._green_roof_green` | green | 18 min | 09:50 | Test job: watch it all. It uses the same green as the grass |
| | 10:00 | `02_site_..._south_half_4_colours` | all 4 | 4.7 h | 14:45 | The campus buildings half |
| **B** | 09:30 | `03_site_..._north_half_4_colours` | all 4 | 6.1 h | 15:40 | Your building, carports and pond. Start by 10:30 at the latest |
| (instead) | 10:00 | `alt_site_model_1to1000_single_colour` | 1 (white) | 6.5 h | 16:30 | Plan C: the whole site in one piece and one colour, painted afterwards. Use it if the halves keep failing or you can only get one day |

The two days don't need to be back to back.

During the 4-colour jobs, the printer cuts and spits out a little blob of plastic at the back
every time it changes colour. That's normal, and the times above include it.

**Joining the halves:**
- Glue both halves to a stiff board (foam board or thin MDF, about 250 x 250 mm). Push the cut
  edges together on the board. The board is also what you carry it on.
- Lift it by the board, never by the model. The trees are the fragile part.

## City (3D Printing Studio, X1C): four days

Times assume you start at 09:30, with the lab staffed 09:00 to 17:00.

| Day | Start | File on the card | Colour | Takes | Done by | Then check |
|---|---|---|---|---|---|---|
| **1** | 09:30 | `01_building_..._pv_strips_dark_blue` | dark blue | 0.9 h | 10:30 | Test job: watch it all |
| | 10:45 | `02_building_..._roofs_grey` | light grey | 3.8 h | 14:35 | The PV strips drop into the roof pockets |
| **2** | 09:30 | `03_building_..._ground_floor_cycle_hub_white` | white | 4.5 h | 14:00 | |
| | 14:15 | `04_furniture_..._trays_3_light_grey` | light grey | 1.4 h | 15:40 | |
| **3** | 09:30 | `05_building_..._first_floor_white` | white | 4.0 h | 13:30 | The first floor sits on the ground floor's pegs, and the roof sits on the first floor |
| | 13:45 | `06_furniture_..._trays_2_light_grey` | light grey | 2.4 h | 16:10 | |
| **4** | 09:30 | `07_furniture_..._trays_1_light_grey` | light grey | 3.1 h | 12:40 | The trays drop into their rooms |
| **5 to 7** | | Spare days: reprint anything that failed, then assemble | | | | |

If you can stay later or the lab allows evening prints, days 3 and 4 combine.

### Why this order

1. **Cheapest first.** The test jobs (PV strips at City, green roof at Clifton) take under an
   hour and use pennies of plastic. A dirty plate or wrong setting shows up there, not on a
   4-hour job.
2. **Fit checks early.** The roofs come straight after the PV strips, so you can check the strips
   fit their pockets on day 1. The first floor follows the ground floor, so you can check the pegs
   on day 3. If something's tight, there's time to sand it or reprint.
3. **The building before the extras.** The building is the main demonstration, so it's finished
   by day 3. If time runs out, cut the furniture first, then fall back to the one-colour site.
4. **Spare days at the end.** Assume at least one job fails. It's normal.

### Getting the building to Clifton

Wrap each floor, the roof and the cycle hub separately in bubble wrap, and put them flat in a box.
The furniture trays have tiny chair backs and table legs, so put them in a small tub with tissue
between them. Glue the PV strips and the green roof on **after** the trip, not before.

### Filament to have ready

**Clifton (X1E AMS):**

| Colour | Needed for | Amount |
|---|---|---|
| Green | Grass (+ the green roof) | 219 g + 9 g |
| Light grey | Roads, paths and existing buildings | 43 g |
| Dark green | Trees | 47 g |
| Orange | Your building and carports on the site | 15 g |

For the one-colour site instead, you need 248 g of any one colour.

**City (X1C):**

| Colour | Needed for | Amount |
|---|---|---|
| White | Ground floor, first floor | 382 g |
| Light grey | Roofs, 3 furniture trays | 293 g |
| Dark blue (black is fine) | PV strips | 22 g |

A full spool is 1 kg. Before each job, check the spool has clearly more left than the job needs.
A spool that looks a quarter full has about 250 g.

---

## How to launch a print, step by step

Do this the same way every time. It takes about 5 minutes. If anything on the screen doesn't
match what's written here, **stop and ask a technician**: asking is free, a crashed print isn't.
Button names can differ slightly between firmware versions.

### Before you go (at home)

1. **Prepare a microSD card.** Any card up to 32 GB that's formatted FAT32 works; most are by
   default. Some labs keep a card in each printer, so ask.
2. **Copy the files onto it.** Copy the **contents** of `sd_card_City_X1C/` or
   `sd_card_Clifton_RISE_X1E/` (whichever campus you're going to). Put the files at the **top
   level of the card**, not inside a folder. If you only have one card, wipe it between campuses:
   the City and Clifton files look alike but are made for different printers.
3. **Open the `plates/` folder on your phone.** It has a picture of every job, so at the printer
   you can check you've picked the right file.

### At the printer

1. **Right printer?** Read the model name on the front: **X1 Carbon** or **X1E**. Use the files
   from the matching folder. If the printer says the file was made for a different printer,
   cancel.
2. **Is it empty and idle?** There should be nothing on the bed and no job running on the screen.
3. **Check the build plate.** It's the removable metal sheet on the bed, and it should be the
   **textured PEI plate** (rough, gold/black).
   - It must be clean. Fingerprints and old plastic stop prints sticking. Hold it by the edges
     only. If it looks greasy, ask how the lab cleans it (usually washing-up liquid and water, or
     an isopropyl alcohol wipe).
   - It must sit flat, with the two notches at the back hooked over the two pins at the back of
     the bed.
4. **Load the filament.**
   - **With an AMS** (the box with 4 spools): put your spool in a slot. Bambu spools are
     detected automatically. For other brands, tap that slot on the screen and set the type to
     **PLA** and the colour.
   - **Without an AMS:** the spool goes on the holder at the back, and you load it from the
     screen (Filament, then Load). Ask a technician to show you the first time.
   - Check there's enough on the spool for the job (see the table above).
5. **Door and lid.** For PLA, Bambu recommends leaving the front door open or the top glass lid
   lifted, so heat doesn't build up and clog the nozzle. Labs often have their own rule, so ask
   once. On the X1E, chamber heating should be **off** for PLA.
6. **Insert the card** into the slot next to the touchscreen.
7. **Pick the file.** On the touchscreen, tap the **Files** (folder) icon, choose the **SD card**,
   and tap your file. **Check the preview picture** matches the one in `plates/`, and that the
   time and weight roughly match the timetable.
8. **On the print-settings screen:**
   - **Bed levelling:** on.
   - **Flow dynamics calibration:** on (or "auto").
   - **Timelapse:** off (it just fills the card).
   - **Use AMS:** on if your spool is in the AMS, off if it's on the back holder.
   - **Filament mapping:** the file shows the colour(s) it expects. Tap each one and choose the
     AMS slot holding that colour. For one-colour jobs there's only one to set.
   - If it warns about the **plate type** or **nozzle size** (these files are for a 0.4 mm
     nozzle), **stop and ask**. Don't press through warnings.
9. **Press Print.** For 5 to 10 minutes it heats up, probes the bed and wipes the nozzle, with
   lots of noises and no plastic yet. That's normal.
10. **Watch the first layer** (the first 10 minutes of actual printing).
    - **Good:** thin flat lines, stuck down, neatly side by side.
    - **Bad:** lines curling up, being dragged around, blobs, nothing coming out, or a
      bird's-nest tangle. If you see that, tap **Pause** or **Stop** on the screen and ask a
      technician. A stopped print only wastes a few grams.
11. **Come back before it finishes.** The screen shows the time remaining. The X1 printers pause
    themselves if the filament runs out or they spot a failed print, so check the screen if it
    seems to have stopped.
12. **Take the parts off.**
    - Wait a few minutes after it finishes, so the plate cools.
    - Lift the plate off the magnetic bed and gently flex it. The parts pop off.
    - Don't dig at the plate with tools, and don't bend it sharply.
    - Put the plate back clean.
13. **Check the part against the "Then check" column** before you start the next job.

### What can actually go wrong

Most mistakes only cost a few grams of plastic and some time:
- **Wrong colour loaded:** reprint.
- **Dirty plate, so it doesn't stick:** clean it and restart.
- **Stopping a job early:** nothing breaks.

The expensive mistakes are rare, and the steps above avoid them:
- **Printing with the wrong nozzle size or filament type.** Step 8 catches that: don't ignore
  warnings.
- **Forcing parts off with metal tools.** That damages the plate.
- **Leaving a failed print running for hours** while it builds a bird's nest around the nozzle.
  Watch the first layer, and check back during long jobs.
