/* Mechanical export and validation of imagegen artwork; no art generation. */
const fs=require('node:fs/promises');
const path=require('node:path');
const crypto=require('node:crypto');
const sharp=require('sharp');
const root=path.resolve(__dirname,'..');
const art=path.join(root,'docs/artwork/post2023');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const read=async p=>JSON.parse(await fs.readFile(p,'utf8'));
const write=async(p,v)=>{await fs.mkdir(path.dirname(p),{recursive:true});await fs.writeFile(p,JSON.stringify(v,null,2)+'\n');};
function bounds(data,w,h,channels,threshold=0){let l=w,t=h,r=-1,b=-1;for(let y=0;y<h;y++)for(let x=0;x<w;x++){if(data[(y*w+x)*channels+channels-1]<=threshold)continue;l=Math.min(l,x);t=Math.min(t,y);r=Math.max(r,x);b=Math.max(b,y);}if(r<l)throw Error('Empty alpha');return{left:l,top:t,width:r-l+1,height:b-t+1};}
async function exportPng(source){
 const raw=await sharp(source).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 let minAlpha=255;for(let i=raw.info.channels-1;i<raw.data.length;i+=raw.info.channels)minAlpha=Math.min(minAlpha,raw.data[i]);
 if(minAlpha!==0)throw Error('Master lacks transparent background');
 const crop=bounds(raw.data,raw.info.width,raw.info.height,raw.info.channels,1);
 const scaled=await sharp(source).extract(crop).resize(168,108,{fit:'inside',kernel:'lanczos3'}).png().toBuffer({resolveWithObject:true});
 return sharp({create:{width:170,height:150,channels:4,background:{r:0,g:0,b:0,alpha:0}}}).composite([{input:scaled.data,left:Math.floor((170-scaled.info.width)/2),top:Math.floor((110-scaled.info.height)/2)}]).png({compressionLevel:9}).toBuffer();
}
async function auditPng(bytes){const m=await sharp(bytes).metadata();if(m.width!==170||m.height!==150||m.channels!==4||!m.hasAlpha)throw Error('Expected170x150RGBA');const {data,info}=await sharp(bytes).raw().toBuffer({resolveWithObject:true});const box=bounds(data,170,150,4);if(box.top+box.height>110)throw Error('Artwork overlaps label space');let opaque=false;for(let i=3;i<data.length;i+=4)if(data[i]===255)opaque=true;if(!opaque)throw Error('No opaque artwork');return box;}
async function saveResult(recordPath){
 const result=await read(path.resolve(recordPath));
 if(!/^(reform|centre|ekre|isamaa|sde|e200|pp)$/.test(result.party)||!/^\w+$/.test(result.asset_id))throw Error('Invalid asset identity');
 const manifest=await read(path.join(art,result.party,'manifest.json'));
 const asset=manifest.icons.find(a=>a.asset_id===result.asset_id);if(!asset)throw Error('Undeclared asset');
 const metaPath=path.join(art,result.party,'records',result.asset_id+'.json');
 try{await fs.access(metaPath);console.log(result.party+'/'+result.asset_id+' already exported');return;}catch{}
 const sourceBytes=await fs.readFile(result.source),master=path.join(art,result.party,asset.master),texture=path.join(root,asset.texture);
 const png=await exportPng(sourceBytes),box=await auditPng(png),m=await sharp(sourceBytes).metadata();
 await fs.mkdir(path.dirname(master),{recursive:true});await fs.mkdir(path.dirname(texture),{recursive:true});
 for(const target of [master,texture]){try{await fs.access(target);throw Error('Refusing to replace existing asset: '+target);}catch(e){if(e.code!=='ENOENT')throw e;}}
 await fs.copyFile(result.source,master);await fs.writeFile(texture,png);
 await write(metaPath,{party:result.party,asset_id:result.asset_id,source_generation_file:path.basename(result.source),master_size:{width:m.width,height:m.height},master_sha256:sha(sourceBytes),texture_sha256:sha(png),texture_bytes:png.length,artwork_bounds:box,export_method:'Trim transparent padding at alpha >1; Lanczos3 fit168x108; center on transparent170x150, bottom40pixels alpha0.'});
 console.log(result.party+'/'+result.asset_id+': saved master +170x150RGBA; bottom40alpha0');
}
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
async function selectRefinement(recordPath){
 const result=await read(path.resolve(recordPath));
 if(!/^(reform|centre|ekre|isamaa|sde|e200|pp)$/.test(result.party)||!/^\w+$/.test(result.asset_id)||!result.edit_prompt)throw Error('Invalid refinement record');
 const folder=path.join(art,result.party),manifestPath=path.join(folder,'manifest.json'),manifest=await read(manifestPath);
 const icon=manifest.icons.find(a=>a.asset_id===result.asset_id);if(!icon)throw Error('Undeclared refinement asset');
 if(icon.refinements?.some(r=>r.edit_prompt===result.edit_prompt&&r.source_generation_file===path.basename(result.source))){console.log('Refinement already selected');return;}
 const metaPath=path.join(folder,'records',icon.asset_id+'.json'),old=await read(metaPath),oldMaster=icon.master;
 const oldMasterBytes=await fs.readFile(path.join(folder,oldMaster)),oldTexture=await fs.readFile(path.join(root,icon.texture));
 if(sha(oldMasterBytes)!==old.master_sha256||sha(oldTexture)!==old.texture_sha256)throw Error('Refusing to replace changed draft');
 const version=(icon.refinements?.length||0)+2,master=oldMaster.replace(/(?:_v\d+)?\.png$/,`_v${version}.png`),draft=`drafts/EST_${result.party}_2023_${icon.asset_id}_v${version-1}.png`;
 const source=await fs.readFile(result.source),png=await exportPng(source),box=await auditPng(png),m=await sharp(source).metadata();
 for(const target of [path.join(folder,master),path.join(folder,draft)]){try{await fs.access(target);throw Error('Refusing to replace preserved draft: '+target);}catch(e){if(e.code!=='ENOENT')throw e;}}
 await fs.mkdir(path.join(folder,'drafts'),{recursive:true});
 await fs.writeFile(path.join(folder,draft),oldTexture);await fs.copyFile(result.source,path.join(folder,master));
 (icon.previous_drafts??=[]).push({master:oldMaster,texture:draft,export:old});
 (icon.refinements??=[]).push({edit_prompt:result.edit_prompt,reference_master:oldMaster,master,source_generation_file:path.basename(result.source)});icon.master=master;
 const record={party:result.party,asset_id:icon.asset_id,source_generation_file:path.basename(result.source),master_size:{width:m.width,height:m.height},master_sha256:sha(source),texture_sha256:sha(png),texture_bytes:png.length,artwork_bounds:box,export_method:old.export_method};
 await fs.writeFile(path.join(root,icon.texture),png);await write(metaPath,record);await write(manifestPath,manifest);
 console.log(result.party+'/'+icon.asset_id+': selected v'+version+'; previous master, runtime and metadata preserved');
}
function wrap(text,max=25,maxLines=3){let lines=[],line='';for(const word of text.split(/\s+/)){if(line&&(line+' '+word).length>max){lines.push(line);line=word;}else line+=(line?' ':'')+word;}if(line)lines.push(line);if(lines.length>maxLines){lines=lines.slice(0,maxLines);lines[maxLines-1]=lines[maxLines-1].slice(0,max-1)+'…';}return lines;}
function labels(text,x,y,{color='#f5f1df',size=11,max=25}={}){return wrap(text,max).map((line,i)=>`<text x="${x}" y="${y+i*13}" text-anchor="middle" fill="${color}" font-size="${size}" font-family="Arial">${esc(line)}</text>`).join('');}
async function renderParty(tree,manifest){
 const party=tree.party,bytes=await Promise.all(manifest.icons.map(a=>fs.readFile(path.join(root,a.texture))));
 const W=1000,H=90+Math.ceil(bytes.length/5)*155,overlays=[];let svg=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}"><rect width="100%" height="100%" fill="#252b33"/><text x="25" y="30" fill="${tree.brand.color}" font-size="22" font-family="Arial" font-weight="bold">${esc(tree.brand.name)} — 2023 POLICY ICONS</text><text x="25" y="53" fill="#aab7c7" font-size="13" font-family="Arial">32 unique textures ·32 focuses ·170×150RGBA ·40 transparent bottom pixels</text>`;
 for(let i=0;i<bytes.length;i++){const x=(i%5)*200+15,y=75+Math.floor(i/5)*155;overlays.push({input:bytes[i],left:x,top:y});svg+=labels(manifest.icons[i].title,x+85,y+122,{max:27});}svg+='</svg>';
 const base=Buffer.from(svg.replace(/<text[\s\S]*$/,'</svg>'));
 const all=Buffer.from(svg.replace('<rect width="100%" height="100%" fill="#252b33"/>',''));
 await sharp(base).composite([...overlays,{input:all,left:0,top:0}]).png().toFile(path.join(art,party,party+'-icons-preview.png'));
 const maxY=Math.max(...tree.focuses.map(f=>f.y)),TW=1250,TH=90+maxY*170+170;
 const bg=`<svg xmlns="http://www.w3.org/2000/svg" width="${TW}" height="${TH}"><rect width="100%" height="100%" fill="#252b33"/><text x="26" y="34" fill="${tree.brand.color}" font-size="25" font-family="Arial" font-weight="bold">${esc(tree.brand.name)} — 2023 FOCUS TREE</text><text x="26" y="61" fill="#aab7c7" font-size="13" font-family="Arial">Layout preview, not an in-game screenshot ·actual coordinates/prerequisites ·coalition leader palette throughout</text>`;
 const nodes=new Map(tree.focuses.map(f=>[f.focus_id,{...f,left:40+f.x*125,top:90+f.y*170}]));let lines='',texts='',pics=[];
 for(const n of nodes.values()){for(const p of n.parents){const parent=nodes.get(p);if(!parent)throw Error('Unknown prerequisite '+p);const x1=parent.left+85,y1=parent.top+153,x2=n.left+85,y2=n.top-4;const mid=Math.floor((y1+y2)/2);lines+=`<path d="M${x1},${y1}V${mid}H${x2}V${y2}" fill="none" stroke="#657181" stroke-width="1.5"/>`;}
 const index=manifest.icons.findIndex(a=>a.asset_id===n.recommended_asset);if(index<0)throw Error('No image '+n.focus_id);pics.push({input:bytes[index],left:n.left,top:n.top});texts+=labels(n.title,n.left+85,n.top+122,{size:11,max:27});}
 await sharp(Buffer.from(bg+lines+'</svg>')).composite([...pics,{input:Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${TW}" height="${TH}">${texts}</svg>`),left:0,top:0}]).png().toFile(path.join(art,party,party+'-tree-preview.png'));
}
async function finish(checkOnly){
 const catalog=await read(path.join(art,'catalog.json'));let count=0,total=0;const hashes=new Set();
 for(const tree of catalog.trees){const manifestPath=path.join(art,tree.party,'manifest.json'),manifest=await read(manifestPath);
 if(tree.focuses.length!==32||manifest.icons.length!==32||new Set(manifest.icons.map(a=>a.asset_id)).size!==32||new Set(tree.focuses.map(f=>f.recommended_asset)).size!==32)throw Error('Each focus must have its own asset: '+tree.party);
 for(const icon of manifest.icons){
 const assigned=tree.focuses.filter(f=>f.recommended_asset===icon.asset_id);
 if(assigned.length!==1||icon.focus_ids.length!==1||icon.focus_ids[0]!==assigned[0].focus_id||icon.focus_suffixes.length!==1||icon.focus_suffixes[0]!==assigned[0].suffix)throw Error('Focus/asset mapping mismatch: '+tree.party+'/'+icon.asset_id);
 if(icon.texture!==`gfx/interface/goals/EST/EST_${tree.party}_2023_${icon.asset_id}.png`)throw Error('Unexpected texture path: '+icon.texture);
 const record=await read(path.join(art,tree.party,'records',icon.asset_id+'.json'));const master=await fs.readFile(path.join(art,tree.party,icon.master)),texture=await fs.readFile(path.join(root,icon.texture));
 if(sha(master)!==record.master_sha256||sha(texture)!==record.texture_sha256)throw Error('Hash mismatch '+tree.party+'/'+icon.asset_id);if(hashes.has(record.texture_sha256))throw Error('Duplicateiconpixels '+icon.texture);hashes.add(record.texture_sha256);await auditPng(texture);if(checkOnly){const expected=await exportPng(master);if(!expected.equals(texture))throw Error('Stale export '+icon.texture);}Object.assign(icon,record);count++;total+=texture.length;}
 if(!checkOnly){await write(manifestPath,manifest);await renderParty(tree,manifest);}console.log(tree.party+':32focuses,32unique textures verified');}
 if(count!==224||hashes.size!==224)throw Error('Expected224uniqueicons');
 if(!checkOnly){const cols=5,W=1160,H=80+catalog.trees.length*160,overlays=[];let svg=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}"><rect width="100%" height="100%" fill="#252b33"/><text x="25" y="33" fill="#f5f1df" font-family="Arial" font-size="25" font-weight="bold">ESTONIA — SEVEN POST-2023 GOVERNMENTS</text><text x="25" y="58" fill="#aab7c7" font-family="Arial" font-size="14">224 focuses ·224 unique party-colored textures ·selected native-size icons from each complete set</text>`;
 for(let r=0;r<catalog.trees.length;r++){const tree=catalog.trees[r],m=await read(path.join(art,tree.party,'manifest.json')),chosen=[m.icons[0],m.icons.find(a=>/air_defence/.test(a.asset_id))||m.icons[1],m.icons.find(a=>a.asset_id==='defence_industry')||m.icons[2],m.icons.find(a=>a.asset_id!=='mandate'&&a.asset_id!=='report'&&a.political_figure)||m.icons[10],m.icons.at(-1)],y=80+r*160;svg+=`<text x="20" y="${y+54}" fill="${tree.brand.color}" font-family="Arial" font-size="18" font-weight="bold">${esc(tree.brand.name)}</text><text x="20" y="${y+76}" fill="#aab7c7" font-family="Arial" font-size="12">32 focuses</text>`;for(let c=0;c<cols;c++){const x=190+c*190;overlays.push({input:await fs.readFile(path.join(root,chosen[c].texture)),left:x,top:y});svg+=labels(chosen[c].title,x+85,y+122,{max:24,size:10});}}svg+='</svg>';const bg=Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}"><rect width="100%" height="100%" fill="#252b33"/></svg>`);await sharp(bg).composite([...overlays,{input:Buffer.from(svg.replace('<rect width="100%" height="100%" fill="#252b33"/>','')),left:0,top:0}]).png().toFile(path.join(art,'seven-governments-preview.png'));}
 console.log((checkOnly?'Verified':'Export review ready:')+' '+count+' textures; '+total+' runtime bytes.');
}
async function main(){if(process.argv[2]==='--save')await saveResult(process.argv[3]);else if(process.argv[2]==='--select-refinement')await selectRefinement(process.argv[3]);else await finish(process.argv.includes('--check'));}
main().catch(e=>{console.error(e.message);process.exitCode=1;});
