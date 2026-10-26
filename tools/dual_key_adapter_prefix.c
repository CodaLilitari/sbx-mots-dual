/* Offline host shim by Coda, collaborating with Andrei, 2026-10-23.
 * The separately concatenated retarget algorithm is unmodified OpenJKDF2
 * contributor source from tristamus/OpenJKDF2 ac698316da694490e233907709a1a4422fb6802f.
 * See the accompanying upstream LICENSE.md. This shim only supplies exact
 * named file loading, native text KEY parsing, allocation and output support.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <ctype.h>
#include <stdarg.h>
#include <math.h>
#include <errno.h>
#ifdef _WIN32
#include <direct.h>
#define make_dir(path) _mkdir(path)
#else
#include <sys/stat.h>
#include <strings.h>
#define make_dir(path) mkdir(path,0700)
#endif
#define SITH_KEY_RETARGET 1
#define SITH_DEBUG_STRUCT_NAMES 1
#define _sscanf sscanf
#define _atoi atoi
#define _atof atof
#define __strcmpi strcasecmp
#ifdef _WIN32
#undef __strcmpi
#define __strcmpi _stricmp
#endif
#define RDROID_ALLOC malloc
#define RDROID_FREE free
#define stdString_snprintf snprintf
#define stdPlatform_Printf printf
#define stdPlatform_Memzero32(ptr,n) memset(ptr,0,n)
typedef float flex_t;
typedef struct { float x,y,z; } rdVector3;
typedef struct { float marker_float[8]; int32_t marker_int[8]; } rdMarkers;
typedef struct { float frameNum; uint32_t flags; rdVector3 pos,orientation,vel,angularVelocity; } rdAnimEntry;
typedef struct { char aMeshName[32]; int32_t nodeNum; uint32_t numEntries; rdAnimEntry *aEntries; } rdJoint;
typedef struct rdKeyframe {
 char name[32]; uint32_t namecrc,id,flags,numJoints,type; float fps; uint32_t numFrames,numJoints2;
 rdJoint *aNodes; uint32_t numMarkers; rdMarkers markers;
 uint32_t upperType,upperNumFrames,upperSrc; float upperFps; int bTurnBlend;
} rdKeyframe;
static int jkRes_bGameFilesOnly=0,stdConffile_linenum=0;
static char stdConffile_g_aLine[16384];
static FILE *conf;
static char input_root[4096],output_root[4096];
static void stdString_SafeStrCopy(char *dst,const char *src,size_t len) {
 if(!len)return;
 size_t n=strlen(src);if(n>=len)n=len-1;memcpy(dst,src,n);dst[n]=0;
}
static uint32_t stdCrc32(const char *data,size_t n) {
 uint32_t crc=~0u; for(size_t i=0;i<n;i++){crc^=(unsigned char)data[i];for(int j=0;j<8;j++)crc=(crc>>1)^(0xedb88320u&-(crc&1u));} return ~crc;
}
static FILE *open_member(const char *name) {
 char normalized[512],path[8192]; size_t n=strlen(name);
 if(n>=sizeof(normalized)||strstr(name,"..")||strchr(name,':'))return NULL;
 for(size_t i=0;i<=n;i++)normalized[i]=name[i]=='\\'?'/':(char)tolower((unsigned char)name[i]);
 FILE *f=NULL;
 if(!jkRes_bGameFilesOnly){snprintf(path,sizeof(path),"%s/overlay/%s",input_root,normalized);f=fopen(path,"rb");}
 if(!f){snprintf(path,sizeof(path),"%s/retail/%s",input_root,normalized);f=fopen(path,"rb");}
 return f;
}
static int stdConffile_Open(const char *name) {
 if(conf){fprintf(stderr,"Nested conf open refused\n");exit(3);} conf=open_member(name);stdConffile_linenum=0;return conf!=NULL;
}
static int stdConffile_ReadLine(void) {
 while(conf&&fgets(stdConffile_g_aLine,sizeof(stdConffile_g_aLine),conf)) {
  stdConffile_linenum++; char *comment=strchr(stdConffile_g_aLine,'#'); if(comment)*comment=0;
  int nonspace=0;for(char *p=stdConffile_g_aLine;*p;p++){*p=(char)tolower((unsigned char)*p);if(!isspace((unsigned char)*p))nonspace=1;}
  if(nonspace)return 1;
 } return 0;
}
static void stdConffile_Close(void){if(conf)fclose(conf);conf=NULL;}
static void rdKeyframe_NewEntry(rdKeyframe *key){memset(key,0,sizeof(*key));}
static void rdKeyframe_FreeEntry(rdKeyframe *key){if(key->aNodes){for(uint32_t i=0;i<key->numJoints2;i++)free(key->aNodes[i].aEntries);free(key->aNodes);}memset(key,0,sizeof(*key));}
static int next_data(FILE *f,char *line,size_t capacity){
 while(fgets(line,(int)capacity,f)){char *c=strchr(line,'#');if(c)*c=0;int used=0;for(char *p=line;*p;p++){*p=(char)tolower((unsigned char)*p);if(!isspace((unsigned char)*p))used=1;}if(used)return 1;}return 0;
}
static int rdKeyframe_LoadEntry(const char *name,rdKeyframe *key){
 FILE *f=open_member(name);char line[4096];int node=-1,read_entries=0;unsigned int declared_nodes=0,actual_nodes=0;
 rdKeyframe_NewEntry(key);if(!f){fprintf(stderr,"Missing KEY %s\n",name);return 0;}
 while(next_data(f,line,sizeof(line))){
  unsigned int val;int ix;
  if(sscanf(line," flags %x",&val)==1){key->flags=val;continue;}
  if(sscanf(line," type %x",&val)==1){key->type=val;continue;}
  if(sscanf(line," frames %u",&val)==1){key->numFrames=val;continue;}
  if(sscanf(line," fps %f",&key->fps)==1)continue;
  if(sscanf(line," joints %u",&val)==1){if(val<1||val>64)goto fail;key->numJoints=key->numJoints2=val;key->aNodes=calloc(val,sizeof(rdJoint));if(!key->aNodes)goto fail;continue;}
  if(sscanf(line," nodes %u",&declared_nodes)==1)continue;
  if(sscanf(line," markers %u",&val)==1){if(val>8)goto fail;key->numMarkers=val;for(unsigned int j=0;j<val;j++){if(!next_data(f,line,sizeof(line))||sscanf(line," %f %d",&key->markers.marker_float[j],&key->markers.marker_int[j])!=2)goto fail;}continue;}
  if(sscanf(line," node %d",&ix)==1){if(ix<0||ix>=(int)key->numJoints||!key->aNodes)goto fail;node=ix;key->aNodes[node].nodeNum=node;actual_nodes++;read_entries=0;continue;}
  if(node>=0&&sscanf(line," mesh name %31s",key->aNodes[node].aMeshName)==1)continue;
  if(node>=0&&sscanf(line," entries %u",&val)==1){if(!val||val>65536||key->aNodes[node].aEntries)goto fail;key->aNodes[node].numEntries=val;key->aNodes[node].aEntries=calloc(val,sizeof(rdAnimEntry));continue;}
  if(node>=0&&sscanf(line," %d:",&ix)==1){rdJoint *j=&key->aNodes[node];if(ix!=read_entries||ix>=(int)j->numEntries||!j->aEntries)goto fail;rdAnimEntry *e=&j->aEntries[ix];
   if(sscanf(line," %d: %f %x %f %f %f %f %f %f",&ix,&e->frameNum,&e->flags,&e->pos.x,&e->pos.y,&e->pos.z,&e->orientation.x,&e->orientation.y,&e->orientation.z)!=9)goto fail;
   if(!next_data(f,line,sizeof(line))||sscanf(line," %f %f %f %f %f %f",&e->vel.x,&e->vel.y,&e->vel.z,&e->angularVelocity.x,&e->angularVelocity.y,&e->angularVelocity.z)!=6)goto fail;
   read_entries++;continue;
  }
 }
 fclose(f);if(!key->aNodes||!key->fps||!key->numFrames||actual_nodes!=declared_nodes)goto fail_closed;return 1;
fail:fclose(f);
fail_closed:rdKeyframe_FreeEntry(key);fprintf(stderr,"Invalid native KEY %s\n",name);return 0;
}
