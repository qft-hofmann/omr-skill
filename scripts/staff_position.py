#!/usr/bin/env python3
"""Convert manually supplied local staff geometry into a written diatonic pitch."""
import argparse, json, math, statistics
BOTTOM={'treble':('E',4),'bass':('G',2),'alto':('F',3),'tenor':('D',3)}
STEPS='CDEFGAB'
def compute(lines,head,clef,tolerance=.30,measurement_error=0.0):
 if len(lines)!=5 or any(not math.isfinite(x) for x in [*lines,head]) or any(a>=b for a,b in zip(lines,lines[1:])):
  raise ValueError('provide exactly five strictly increasing top-to-bottom line coordinates')
 if not (0<tolerance<.5):raise ValueError('tolerance must be between 0 and 0.5')
 if not math.isfinite(measurement_error) or measurement_error<0:raise ValueError('measurement error must be finite and nonnegative')
 if clef not in BOTTOM:raise ValueError('unsupported clef')
 gaps=[b-a for a,b in zip(lines,lines[1:])];spacing=statistics.median(gaps)
 spread=max(abs(g-spacing) for g in gaps)/spacing
 geometry_ok=spread<=.15 # warning heuristic, not calibrated recognition confidence
 q=2*(lines[-1]-head)/spacing;nearest=math.floor(q+.5);residual=q-nearest
 eps=measurement_error
 if spacing<=2*eps:interval=None;geometry_ok=False
 else:
  qs=[2*x/d for x in [lines[-1]-head-2*eps,lines[-1]-head+2*eps] for d in [spacing-2*eps,spacing+2*eps]]
  interval=[min(qs),max(qs)]
 rounding=abs(residual)>=tolerance or interval is None or math.floor(interval[0]+.5)!=math.floor(interval[1]+.5)
 letter,octave=BOTTOM[clef];index=octave*7+STEPS.index(letter)+nearest
 return {'clef':clef,'line_y_top_to_bottom':lines,'head_y':head,'local_line_spacing':spacing,'line_spacing_range':[min(gaps),max(gaps)],'geometry_consistent':geometry_ok,'relative_gap_deviation':spread,'diatonic_step_unrounded':q,'nearest_step':nearest,'residual_steps':residual,'measurement_error_px':eps,'step_interval':interval,'rounding_ambiguous':rounding,'written_diatonic_pitch':f'{STEPS[index%7]}{index//7}' if geometry_ok else None,'ambiguous':not geometry_ok or rounding,'limitations':'Geometry and rounding diagnostics, not recognition confidence. Inspect head and staff identity, clef, accidentals and transposition. The 15% gap threshold is a warning heuristic; zero input error does not mean perfect measurement.'}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lines',type=float,nargs=5,required=True,metavar=('TOP','L2','L3','L4','BOTTOM'));p.add_argument('--head',type=float,required=True);p.add_argument('--clef',choices=sorted(BOTTOM),required=True);p.add_argument('--tolerance',type=float,default=.30)
 p.add_argument('--measurement-error',type=float,default=0.0)
 a=p.parse_args()
 try:print(json.dumps(compute(a.lines,a.head,a.clef,a.tolerance,a.measurement_error),indent=2,allow_nan=False))
 except ValueError as e:p.error(str(e))
if __name__=='__main__':main()
