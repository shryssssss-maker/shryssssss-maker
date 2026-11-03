"""Compact GPU-generated orbital lookup animation for the exact source texture.

Every source texel follows a radius-dependent elliptical orbit or a ridge
streamline. Two lit cohorts provide continuous forward motion at the loop seam.
Coarse/fine lookup pairs retain subpixel precision without storing noisy RGB
frames. There is no fluid/noise displacement or rigid rotating picture layer.
"""
from pathlib import Path
import sys,io,base64,json,gzip,time,os,tempfile
import cupy as cp
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter
from scipy.interpolate import PchipInterpolator

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT;DESIGN=OUT/'design'
_cache=ROOT/'.render-cache';(_cache/'tmp').mkdir(parents=True,exist_ok=True)
os.environ.setdefault('CUPY_CACHE_DIR',str(_cache/'kernels'))
tempfile.tempdir=str(_cache/'tmp')
W,H=1136,1384;MW,MH=142,173;N=120;FPS=30
mi=Image.new('L',(W,H));d=ImageDraw.Draw(mi)
d.polygon([(376,112),(570,106),(W,106),(W,491),(506,508),(167,499),(163,453),(329,395),(375,331)],fill=255)
d.rectangle((0,1184,W,H),fill=255)
mask=gaussian_filter(np.asarray(mi,dtype=np.float32)/255,3)
mask[40:107,:]=0;mask[355:451,65:351]=0;mask[509:1181,:]=0;mask[1260:1324,865:1111]=0
ridge=np.array([(0,1304),(98,1264),(132,1284),(193,1268),(264,1233),(327,1259),(391,1271),(455,1257),(509,1293),(571,1301),(641,1286),(699,1313),(790,1324),(900,1345),(1050,1358),(1136,1359)],np.float32)
curve=PchipInterpolator(ridge[:,0],ridge[:,1])
assert curve.c.shape==(4,15), "Update the CUDA ridge coefficient layout when changing ridge knots"

CODE=r'''
__device__ float ridge_at(float x,const float* knots,const float* coeff){
 x=fminf(1136.f,fmaxf(0.f,x));int j=0;while(j<14&&x>knots[j+1])j++;
 float t=x-knots[j];return ((coeff[j]*t+coeff[15+j])*t+coeff[30+j])*t+coeff[45+j];
}
__device__ float smooth(float a,float b,float x){float t=fminf(1.f,fmaxf(0.f,(x-a)/(b-a)));return t*t*(3-2*t);}
extern "C" __global__ void orbital_map(float* result,const float* allowed,
 const float* knots,const float* coeff,int mw,int mh,float phase){
 int i=blockDim.x*blockIdx.x+threadIdx.x;if(i>=mw*mh)return;
 float x=(i%mw+.5f)*1136.f/mw-.5f,y=(i/mw+.5f)*1384.f/mh-.5f;
 int ix=(int)fminf(1135.f,fmaxf(0.f,roundf(x))),iy=(int)fminf(1383.f,fmaxf(0.f,roundf(y)));
 float strength=allowed[iy*1136+ix];float sx=x,sy=y;
 if(strength>.00001f){
   if(y>1180){
     float sunx=x-147.f,suny=y-1222.f,rr=sunx*sunx+suny*suny;
     float hs=x-72.f*phase;
     float depth=(y-ridge_at(x,knots,coeff))/(1.15f-.30f*x/1136.f);
     float hy=ridge_at(hs,knots,coeff)+depth*(1.15f-.30f*hs/1136.f);
     hy-=.65f*(sinf(phase*6.2831853f+hs*.015f)-sinf(hs*.015f));
     float sun=1.f-smooth(144.f,324.f,rr);
     float a=-phase*.18f,c=cosf(a),s=sinf(a);
     float sun_sx=147.f+c*sunx-s*suny,sun_sy=1222.f+s*sunx+c*suny;
     sx=hs*(1-sun)+sun_sx*sun;sy=hy*(1-sun)+sun_sy*sun;
   }else{
     float angle=-.401425728f,c=cosf(angle),s=sinf(angle);
     float dx=x-752.f,dy=y-293.f,u=c*dx+s*dy,v=-s*dx+c*dy;
     float r=hypotf(u,v/.26f),phi=atan2f(v/.26f,u),oldphi=phi;
     for(int j=0;j<4;j++){
       float tangent=fmaxf(1.f,hypotf(r*sinf(oldphi),r*.26f*cosf(oldphi)));
       float wave=sinf(r*.017f+2*oldphi);
       float step=fminf(.4f,(65.f+30.f*wave*wave)/tangent);
       oldphi=phi-phase*step;
     }
     float ox=r*cosf(oldphi),oy=r*.26f*sinf(oldphi);
     float dsx=752.f+c*ox-s*oy,dsy=293.f+s*ox+c*oy;
     float rad2=dx*dx+dy*dy;
     float body=1.f-smooth(145.f*145.f,151.f*151.f,rad2);
     float band=(1.f-smooth(14.f,25.f,fabsf(y-(630.f-.37f*x))))*smooth(604.f,620.f,x)*(1.f-smooth(895.f,910.f,x));
     body*=1.f-band;
     float rx=sqrtf(fmaxf(1.f,138.8f*138.8f-dy*dy));
     float theta=asinf(fminf(.99999f,fmaxf(-.99999f,dx/rx)));
     float step=fminf(.065f,4.5f/fmaxf(1.f,rx*cosf(theta)));
     float edge=1.f-smooth(132.f*132.f,138.8f*138.8f,rad2);
     float bsx=x+(752.f+rx*sinf(theta+phase*step)-x)*edge;
     sx=dsx*(1-body)+bsx*body;sy=dsy*(1-body)+y*body;
   }
 }
 result[2*i]=(sx-x)*strength;result[2*i+1]=(sy-y)*strength;
}
'''

device=cp.cuda.Device(0);device.use();name=cp.cuda.runtime.getDeviceProperties(0)['name'];name=name.decode() if isinstance(name,bytes) else str(name)
kernel=cp.RawKernel(CODE,'orbital_map',options=('--std=c++17',));kernel.compile()
gm=cp.asarray(mask);gk=cp.asarray(np.ascontiguousarray(ridge[:,0]));gc=cp.asarray(np.ascontiguousarray(curve.c,dtype=np.float32));go=cp.empty((MH,MW,2),np.float32)
print('Rendering orbital lookups on',name,flush=True)

def encode_pair(displacement):
    coarse=np.clip(np.rint(128+displacement*.5),0,255).astype(np.uint8)
    represented=(coarse.astype(np.float32)-128)*2
    # Correct the residual after the coarse sampler, including its local
    # Jacobian, so a 2px coarse unit does not quantize the moving grain.
    dx=W/MW;dy=H/MH
    ux=np.gradient(represented[:,:,0],dx,axis=1);uy=np.gradient(represented[:,:,0],dy,axis=0)
    vx=np.gradient(represented[:,:,1],dx,axis=1);vy=np.gradient(represented[:,:,1],dy,axis=0)
    ex=displacement[:,:,0]-represented[:,:,0];ey=displacement[:,:,1]-represented[:,:,1]
    det=(1+ux)*(1+vy)-uy*vx;det=np.where(np.abs(det)<.2,np.copysign(.2,det),det)
    residual=np.stack((((1+vy)*ex-uy*ey)/det,((1+ux)*ey-vx*ex)/det),axis=-1)
    fine=np.clip(np.rint(128+residual*32),0,255).astype(np.uint8)
    neutral=np.full((MH,MW,3),128,np.uint8)
    c=neutral.copy();c[:,:,:2]=coarse
    f=neutral.copy();f[:,:,:2]=fine
    return Image.fromarray(c),Image.fromarray(f)

streams={k:[] for k in ['coarseA','fineA','coarseB','fineB']}
start=time.time()
for i in range(N):
    for suffix,phase in [('A',i/N),('B',i/N-1)]:
        kernel(((MW*MH+255)//256,),(256,),(go,gm,gk,gc,np.int32(MW),np.int32(MH),np.float32(phase)))
        c,f=encode_pair(cp.asnumpy(go));streams['coarse'+suffix].append(c);streams['fine'+suffix].append(f)
    if i%30==0:print('GPU frames',i,'/',N,flush=True)
duration=[round((i+1)*1000/FPS)-round(i*1000/FPS) for i in range(N)]
atlas=[]
for i in range(N):
    frame=Image.new('RGB',(MW*3,MH*2))
    frame.paste(streams['coarseA'][i],(0,0));frame.paste(streams['fineA'][i],(MW,0))
    frame.paste(streams['coarseB'][i],(0,MH));frame.paste(streams['fineB'][i],(MW,MH))
    weight=round(i/N*255)
    frame.paste((255-weight,)*3,(MW*2,0,MW*3,MH))
    frame.paste((weight,)*3,(MW*2,MH,MW*3,MH*2))
    atlas.append(frame)
b=io.BytesIO();atlas[0].save(b,format='PNG',save_all=True,append_images=atlas[1:],duration=duration,loop=0,optimize=True)
url='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
print('Synchronized orbital atlas',len(b.getvalue()),'bytes',flush=True)
manifest={'gpu':name,'frames':N,'fps':FPS,'seconds':N/FPS,'coarse_scale':510,'fine_scale':7.96875,'source_offset_coarse':1,'source_offset_fine':.015625,'atlas':url,'atlas_grid':[3,2],'model':'radius-dependent independent elliptical advection of source pixels; source-preserving moving cohorts; actual hill ridge streamlines'}
with gzip.open(DESIGN/'orbital-lookups.json.gz','wt',encoding='utf-8',compresslevel=9) as f:json.dump(manifest,f,separators=(',',':'))
print('GPU lookup rendering and encoding seconds:',time.time()-start,flush=True)
