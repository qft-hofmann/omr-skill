import importlib.util
import unittest
from pathlib import Path
module=Path(__file__).parents[1]/'scripts'/'staff_position.py'
spec=importlib.util.spec_from_file_location('staff_position',module)
pitch=importlib.util.module_from_spec(spec);spec.loader.exec_module(pitch)
class StaffPositionTests(unittest.TestCase):
 def test_treble_lines_spaces_and_ledger(self):
  lines=[100,110,120,130,140]
  for y,expected in [(140,'E4'),(135,'F4'),(130,'G4'),(120,'B4'),(95,'G5'),(80,'C6'),(150,'C4')]:
   self.assertEqual(pitch.compute(lines,y,'treble')['written_diatonic_pitch'],expected)
 def test_clefs(self):
  for clef,expected in [('bass','G2'),('alto','F3'),('tenor','D3')]:
   self.assertEqual(pitch.compute([100,110,120,130,140],140,clef)['written_diatonic_pitch'],expected)
 def test_boundary_needs_review(self):
  r=pitch.compute([100,110,120,130,140],137.5,'treble')
  self.assertTrue(r['ambiguous']);self.assertAlmostEqual(r['diatonic_step_unrounded'],.5)
 def test_measured_scan_regression(self):
  r=pitch.compute([213,230,247,264,281],177,'treble');self.assertEqual(r['written_diatonic_pitch'],'C6')
 def test_bad_geometry_rejected(self):
  for lines in ([1,2,3,4],[1,2,2,4,5]):
   with self.assertRaises(ValueError):pitch.compute(lines,2,'treble')
 def test_inconsistent_lines_do_not_yield_settled_pitch(self):
  result=pitch.compute([100,110,120,130,150],120,'treble')
  self.assertFalse(result['geometry_consistent']);self.assertTrue(result['ambiguous'])
  self.assertIsNone(result['written_diatonic_pitch'])
 def test_measurement_error_can_cross_pitch_boundary(self):
  self.assertTrue(pitch.compute([100,110,120,130,140],120,'treble',measurement_error=2)['rounding_ambiguous'])
 def test_nonfinite_input(self):
  with self.assertRaises(ValueError):pitch.compute([100,110,120,130,float('inf')],120,'treble')
if __name__=='__main__':unittest.main()
