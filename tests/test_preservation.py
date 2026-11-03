import copy
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from score_compare import inventory, compare, iter_notes
from apply_annotations import apply

SCORE = '''<score-partwise><part-list/><part id="P1"><measure number="0"><attributes><divisions>4</divisions><key><fifths>0</fifths></key><time><beats>2</beats><beat-type>4</beat-type></time><clef><sign>G</sign><line>2</line></clef></attributes><note><pitch><step>D</step><octave>4</octave></pitch><duration>1</duration><voice>1</voice><type>16th</type><beam number="1">begin</beam><beam number="2">begin</beam><notations><technical><fingering>2</fingering></technical></notations></note><note><pitch><step>E</step><octave>4</octave></pitch><duration>1</duration><voice>1</voice><type>16th</type><beam number="1">end</beam><beam number="2">end</beam></note><note><rest/><duration>6</duration><voice>1</voice><type>quarter</type><dot/></note></measure></part></score-partwise>'''

class PreservationTests(unittest.TestCase):
 def inv(self,root):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.xml';ET.ElementTree(root).write(p);return inventory(p)
 def test_secondary_beam_spelling_voice_and_attachments(self):
  root=ET.fromstring(SCORE);base=self.inv(root)
  for field in ['beam','spelling','voice','fingering','rest','accidental','tie']:
   changed=copy.deepcopy(root);n=changed.find('.//note')
   if field=='beam':n.find("beam[@number='2']").text='forward hook'
   elif field=='spelling':n.find('pitch/step').text='C';ET.SubElement(n.find('pitch'),'alter').text='2'
   elif field=='voice':n.find('voice').text='2'
   elif field=='fingering':n.find('notations/technical/fingering').text='3'
   elif field=='rest':changed.findall('.//note')[2].set('print-object','no')
   elif field=='accidental':ET.SubElement(n,'accidental',cautionary='yes').text='natural'
   else:ET.SubElement(n,'tie',type='start')
   with self.subTest(field=field):self.assertFalse(compare(base,self.inv(changed))['equal'])
 def test_layout_only_change(self):
  a=ET.fromstring(SCORE);b=copy.deepcopy(a);b.find('.//note/pitch').set('default-x','123')
  self.assertTrue(compare(self.inv(a),self.inv(b))['equal'])
 def test_annotation_attachment_guard_and_idempotence(self):
  root=ET.fromstring(SCORE);target=next(iter_notes(root))[0]
  annotations={'version':1,'notes':[{'target':target,'replace':{'notations/technical/fingering':['<fingering>4</fingering>'],'beam':['<beam number="1">begin</beam>','<beam number="2">forward hook</beam>']}}]}
  once=apply(root,annotations);one=self.inv(once);two=self.inv(apply(once,annotations))
  self.assertTrue(compare(one,two)['equal']);self.assertEqual(len(once.findall('.//fingering')),1)
  wrong=copy.deepcopy(annotations);wrong['notes'][0]['target']['expect_pitch']='F4'
  with self.assertRaises(ValueError):apply(ET.fromstring(SCORE),wrong)
 def test_annotation_rejects_musical_override_and_duplicate(self):
  root=ET.fromstring(SCORE);target=next(iter_notes(root))[0]
  bad={'version':1,'notes':[{'target':target,'replace':{'pitch':['<pitch/>']}}]}
  with self.assertRaises(ValueError):apply(root,bad)
  record={'target':target,'replace':{'beam':['<beam number="1">begin</beam>']}}
  with self.assertRaises(ValueError):apply(ET.fromstring(SCORE),{'version':1,'notes':[record,record]})
 def test_divisions_normalization(self):
  a=ET.fromstring(SCORE);b=copy.deepcopy(a);b.find('.//divisions').text='8'
  for e in b.findall('.//duration'):e.text=str(int(e.text)*2)
  self.assertTrue(compare(self.inv(a),self.inv(b))['equal'])

if __name__=='__main__':unittest.main()
