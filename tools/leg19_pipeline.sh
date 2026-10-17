#!/bin/sh
# Leg19: regenerate every story map, script and table on a decomp tree. Usage: leg19_pipeline.sh TREE
# (TREE is an unpacked decomp_full_v18+ tree with data/mb_*.gba copied from pret). Then run make -j8 in TREE.
set -e
T=$1; D=$(dirname "$0")
python3 $D/leg5_story_map_objects.py $T
python3 $D/leg7_donor_maps.py $T
python3 $D/leg9_indoor_maps.py $T
python3 $D/leg19_camp.py $T
SCRIPTS_ONLY=1 python3 $D/leg3_story.py $D/../story/chapters.json $T
python3 $D/leg19_levels.py $T /workspace/pokefirered $D/../docs/LEVEL_CURVE.md > /dev/null
