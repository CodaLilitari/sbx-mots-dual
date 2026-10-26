/* Native serialization and explicit retail layering adaptation.
 * select=0: all nodes; select=1: upper; select=-1: lower.
 * Algorithm-produced entries are serialized with nine significant digits,
 * sufficient to reproduce their float32 values when parsed by the engine.
 */
static int write_key(const char *name,rdKeyframe *key,int select,int own_clock){
 char path[8192];snprintf(path,sizeof(path),"%s/%s",output_root,name);FILE *f=fopen(path,"wb");if(!f)return 0;
 uint32_t frames=own_clock?key->upperNumFrames:key->numFrames;
 float fps=own_clock?key->upperFps:key->fps;
 uint32_t count=0;
 for(uint32_t i=0;i<key->numJoints2;i++){int upper=(sithKeyRetarget_state.dst.nodes[i].type&RT_BODY_UPPER)!=0;if(select==1&&!upper)continue;if(select==-1&&upper)continue;count++;}
 fprintf(f,"# Locally derived using OpenJKDF2 retarget source ac698316da694490e233907709a1a4422fb6802f\n# Contains owned JK animation; keep generated output local.\nSECTION: HEADER\nFLAGS 0x%04x\nTYPE 0x%x\nFRAMES %u\nFPS %.9g\nJOINTS %u\nSECTION: MARKERS\n",
         key->flags,select==1?RT_BODY_UPPER:key->type,frames,fps,20u);
 if(own_clock){fprintf(f,"MARKERS 1\n0 4\n");}
 else {fprintf(f,"MARKERS %u\n",key->numMarkers);for(uint32_t i=0;i<key->numMarkers;i++)fprintf(f,"%.9g %d\n",key->markers.marker_float[i],key->markers.marker_int[i]);}
 fprintf(f,"SECTION: KEYFRAME NODES\nNODES %u\n",count);
 for(uint32_t i=0;i<key->numJoints2;i++){
  int upper=(sithKeyRetarget_state.dst.nodes[i].type&RT_BODY_UPPER)!=0;if(select==1&&!upper)continue;if(select==-1&&upper)continue;
  rdJoint *j=&key->aNodes[i];fprintf(f,"NODE %d\nMESH NAME %s\nENTRIES %u\n",j->nodeNum,j->aMeshName,j->numEntries);
  for(uint32_t n=0;n<j->numEntries;n++){rdAnimEntry *e=&j->aEntries[n];fprintf(f,"%u: %.9g 0x%04x %.9g %.9g %.9g %.9g %.9g %.9g\n%.9g %.9g %.9g %.9g %.9g %.9g\n",n,e->frameNum,e->flags,e->pos.x,e->pos.y,e->pos.z,e->orientation.x,e->orientation.y,e->orientation.z,e->vel.x,e->vel.y,e->vel.z,e->angularVelocity.x,e->angularVelocity.y,e->angularVelocity.z);}
 }
 if(fclose(f))return 0;
 return 1;
}
int main(int argc,char **argv){
 if(argc!=3){fprintf(stderr,"usage: dual-key-baker INPUT-STAGING OUTPUT-KEY-DIR\n");return 2;}
 stdString_SafeStrCopy(input_root,argv[1],sizeof(input_root));stdString_SafeStrCopy(output_root,argv[2],sizeof(output_root));
 if(make_dir(output_root)&&errno!=EEXIST){perror(output_root);return 2;}
 sithKeyRetarget_Reset();
 if(sithKeyRetarget_FindKey("rt_bostand.key")<0)return 3;
 int made_upper=0;
 for(int i=0;i<sithKeyRetarget_state.recipe.numKeys;i++){
  const char *name=sithKeyRetarget_state.recipe.outKeys[i];rdKeyframe key;
  if(!sithKeyRetarget_Build(name,&key))return 4;
  int lower=key.upperFps>0;
  if(!write_key(name,&key,lower?-1:0,0))return 5;
  if(lower&&!made_upper){if(!write_key("rt_boupper.key",&key,1,1))return 5;made_upper=1;}
  printf("RETAIL_KEY %s nodes=%u frames=%u fps=%.9g layer=%s upperclock=%u:%.9g\n",name,key.numJoints,key.numFrames,key.fps,lower?"lower":"full",key.upperNumFrames,key.upperFps);
  rdKeyframe_FreeEntry(&key);
 }
 return made_upper?0:6;
}
