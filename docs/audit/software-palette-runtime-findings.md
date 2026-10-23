# Software texture color investigation

The `sbx-candidate08-skinsoft01` screenshots show coherent textured geometry, but Yoda appears ochre and Mara's exposed arms appear dark orange in the dim Carbon Freeze fixture. This investigation does not equate the absence of corruption with color fidelity.

The fixture is the owned MotS `JKM_MP.GOO` map `jkl/mdm02_freezer.jkl`. Its native colormap table references `01narsh.cmp`, and the staged scene contains no loose CMP override. The harness confirms the matching native resource is `JKMRES.GOO:misc/cmp/01narsh.cmp`, SHA-256 `225a8fd38249961eaf46bd0a92eda6a7052111e85b8beaa6ddb4171358a89eb3`. The same bytes were used in the independent lighting-table calculation. There is no evidence of a JK/custom palette substitution.

Mara's `maraarm.mat` and `mara4arm.mat` are already indexed8 in the source and are absent from the software conversion patch. Their existing skin-color indices become orange/brown through native low-light palette ramps. The harness also observes warm exposed arms on the unchanged base Kyle in this fixture.

Yoda's original RGB565 face texture is olive/yellow-green with warm highlights. Its average RGB is `(176.515, 174.235, 77.917)`. The converted texture at full illumination averages `(177.968, 174.812, 77.533)`. Applying the native `01narsh.cmp` light-table level32 to those same output indices gives `(111.684, 80.914, 25.156)`, reproducing the brown hue without a mismatched palette.

In particular, frequently selected greenish native indices115/116 map to brown index169 at that light level. The converter does retain ordinary green choices; it did not exclude every green or mistakenly decode the source as red. Stable RGB entries across map palettes do not imply hue-preserving lighting ramps.

The companion `software-yoda-palette-comparison.png` has four columns: original RGB565 at full illumination; converted indexed texture at full illumination; original RGB multiplied by0.5; converted indices passed through native `01narsh` light-table level32. This is an offline explanatory calculation, not an engine render. Its third column illustrates hue-preserving linear attenuation, which is not what the native indexed renderer does for these colors.

No builder algorithm or API change was made. Constraining Yoda to a greener, darker ramp would deliberately change the source artwork; changing CMP tables would also alter level-wide rendering. A brighter native software control was requested to establish how the source-faithful conversion appears outside this dim fixture. The optional patch must retain the documented limitation that native indexed lighting can shift hues, even when full-light quantization is close to the source.

Source measurements and fixture provenance are in `software-yoda-palette-evidence.json`. The unchanged software builder SHA-256 is `2594d80ae06c82ae61d64740d40c0d1baaee607fb2601ac94fb4d9684c89d2ab`.
