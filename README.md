# CTR NX2

An experimental native Nintendo Switch 2 / kaiHEN port of Crash Team Racing, built on the public CTR decompilation and the ARM64 Apple-platform port. This project is **not an emulator** and does not need a PlayStation BIOS. You must supply your own compatible retail disc images and a Switch 2 already capable of running kaiHEN homebrew.

The repository contains source patches, platform code in those patches, and local build/extraction scripts. It does **not** include game discs, game executables, textures, audio, video, save files, firmware, keys, SDK binaries, or prebuilt game binaries. The scripts extract required data on your own computer; neither disc image is modified or uploaded.

## Where this comes from

The base is [CTRPad](https://github.com/chrissotraidis/ctrpad) at commit `d578636d`, the ARM64 macOS, iPhone and iPad port. CTRPad builds on [CTR Native](https://github.com/CTR-tools/ctr-native) and the [CTR-ModSDK](https://github.com/CTR-tools/CTR-ModSDK) decompilation. CTR NX2 applies the patches in `patches/` to that exact CTRPad revision. It adds a Switch 2 platform layer using [ounce-devkit / libounce](https://github.com/ouncebrew/ounce-devkit), OunceVK and EGL/OpenGL ES, with an SDL3 compatibility layer. SDL3 headers and third-party licenses remain in the upstream CTRPad checkout.

The patch workflow makes the precise upstream base and local changes reviewable and keeps third-party source and game data out of this repository. CTRPad is GPL-3.0 licensed; see [LICENSE](LICENSE), the upstream repository, and its `RIGHTS_AND_LICENSES.md` for the project's licensing and attribution details. Game content and trademarks belong to their respective owners.

## Choose a data profile

| Profile | Discs required | Text | Voices | Build output |
| --- | --- | --- | --- | --- |
| `ntsc` | NTSC-U SCUS-94426 | English | English | `out/ntsc/` |
| `pal` (default) | NTSC-U SCUS-94426 **and** PAL SCES-02105 | English, French, German, Italian, Spanish, Dutch | Spanish for Spanish; English otherwise | `out/` |

Both profiles use the NTSC-U sound-effect banks, XA music, English voices and Scrapbook video. The PAL profile converts the PAL BIGFILE's entry layout to the indices expected by the NTSC-U game code and extracts Spanish voices. PAL and NTSC graphics use different VRAM layouts, so the scripts build separate NROs; do not mix a profile's NRO and assets with the other profile. The NTSC profile does not display the PAL language selector.

## Requirements

- A legally acquired, compatible **raw MODE2/2352 BIN** of the NTSC-U disc. A CUE can describe the image, but pass the matching BIN path to the scripts.
- For the multilingual profile, a raw MODE2/2352 BIN of PAL SCES-02105 as well.
- Git, Python 3, Docker and enough free space for the source checkout, toolchain image, extracted assets, build and SD folder. The scripts do not download disc images.
- A Switch 2 with a working kaiHEN/homebrew environment, a microSD card and a controller.

The toolchain build uses the upstream ounce-devkit Dockerfile pinned by the setup script and runs its image as `linux/amd64` (including on Apple Silicon). Toolchain packages are provided by their upstream repositories; availability and compatibility may change.

## Setup and build

Run the following from a terminal in the repository root. Paths are examples; keep the quotes for paths with spaces.

```sh
# Fetch the public base and apply the patches. Refuses to replace an existing checkout.
./setup-source.sh

# Fetch the pinned ounce-devkit source and build the toolchain image.
./setup-toolchain.sh

# Always required: extract from your own NTSC-U BIN.
python3 -I extract-ntscu.py /path/to/your-ntsc-u.bin
```

For an **English-only** installation:

```sh
MODE=ntsc ./build.sh
MODE=ntsc ./package-sd.sh
```

For the **multilingual** installation, also provide your PAL BIN:

```sh
python3 -I extract-pal.py /path/to/your-pal.bin
MODE=pal ./build.sh
MODE=pal ./package-sd.sh
```

The PAL extractor derives the small font lookup header from the PAL executable locally. It and all extracted data remain under ignored `.cache/`; do not commit or redistribute them. Extraction may require substantial local disk space. `build.sh` uses separate Docker volumes for the profiles; `MODE=ntsc ./build.sh clean` or `MODE=pal ./build.sh clean` removes the selected build volume. Source and extracted assets are kept.

To use a different public CTRPad clone or checkout location for development, set `CTR_SOURCE_URL` and/or `SRC` for `setup-source.sh`; pass the same `SRC` to `build.sh`. The patches are expected to apply to the pinned revision, and setup intentionally refuses to overwrite an existing source directory.

## Install and play

Copy the contents of `out/ntsc/sd/` or `out/sd/` for your chosen profile to the root of the Switch 2 microSD card. The resulting layout is:

```text
switch/ctr-native/
  ctr-native.nro
  ctr-native.ini              # created by the game on first run
  assets/
    BIGFILE.BIG
    SOUNDS/KART.HWL
    TEST.STR
    XA/ENG.XNF
    XA/ENG/{GAME,EXTRA}/...
    XA/MUSIC/...
    XA/SPN.XNF                # multilingual profile only
    XA/SPN/{GAME,EXTRA}/...   # multilingual profile only
```

Launch CTR Native from the homebrew menu. **B** confirms, and pressing **+ and − together** exits to the homebrew menu. Use the game's Options entry to adjust aspect ratio, internal resolution, texture filtering, vibration strength and unlocks. Options are saved in `ctr-native.ini` next to the NRO. The multilingual build shows its language selector on startup; the chosen language is saved. Vibration previews briefly when the setting changes.

Copy only your own locally prepared files to your own console. Never commit or publish the generated `out/` or `.cache/` directories. Save files and logs are kept under the game directory; back them up before replacing an installation.

## Current status and troubleshooting

This is experimental. Basic launch, menus and gameplay have been exercised on Switch 2, but some recent changes and combinations of video mode, language, audio, rumble and hardware remain unverified. In particular, test the aspect-ratio change, option persistence, Scrapbook playback and the rumble preview on your own hardware. Online play from the browser version is not included.

If startup fails, check `stdout.log`, `stderr.log` and `Crash Team Racing.log` next to the NRO. Check that the NRO and assets use the same profile, the image regions match the expected serials, and the full extracted directories were copied. Avoid publishing logs or configuration that may contain personal paths or other private information. If performance is poor, try a lower internal resolution in Options.

For diagnostics only, `capture_swaps` in `ctr-native.ini` can save screenshots next to the NRO; leave it unset for normal play. Mac testing can be launched silently with `SDL_AUDIO_DRIVER=dummy`.
