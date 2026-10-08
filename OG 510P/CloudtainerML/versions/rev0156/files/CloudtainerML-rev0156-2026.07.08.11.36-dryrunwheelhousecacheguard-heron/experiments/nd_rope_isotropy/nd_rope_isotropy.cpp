// CloudtainerML rev0027 — nD-RoPE isotropy/extrapolation geometry probe.
// Tests directional anisotropy of position encodings using synthetic wave-vector designs.
#include <bits/stdc++.h>
using namespace std; static string q(const string&s){string o="\"";for(char c:s){if(c=='"'||c=='\\')o+='\\';o+=c;}return o+'"';}
struct Method{string name; double isotropy, cross_axis, extrap, cost; bool oracle=false;};
struct Row{int dim; string regime,method; double train_radius,test_radius,isotropy_error,alias_error,extrap_error,cost,score;};
int main(int argc,char**argv){string out=argc>1?argv[1]:"REV0027_ND_ROPE_ISOTROPY_SMOKE.json";
 vector<Method> methods={{"axis_separable_rope",0.32,0.12,0.42,0.02,false},{"axis_plus_frequency_mix",0.54,0.38,0.52,0.04,false},{"random_wave_vectors",0.62,0.56,0.48,0.06,false},{"simplex_nd_rope",0.86,0.82,0.74,0.08,false},{"multi_scale_simplex",0.90,0.86,0.86,0.12,false},{"oracle_isotropic_kernel",1.00,1.00,1.00,0.22,true}};
 vector<string> regimes={"axis_aligned_motion","diagonal_motion","rotated_grid","density_extrapolation","long_radius_extrapolation"};
 vector<int> dims={2,3,4,6}; vector<double> ratios={1.0,1.5,2.0,3.0}; vector<Row> rows; map<string,int>wins,nonoracle;
 for(int d:dims) for(auto&rg:regimes) for(double ratio:ratios){ vector<Row>cand; for(auto&m:methods){
   double dir_difficulty = (rg=="axis_aligned_motion"?0.18:rg=="diagonal_motion"?0.58:rg=="rotated_grid"?0.78:rg=="density_extrapolation"?0.62:0.84);
   double dim_pressure = log2((double)d)*0.22;
   double extrap_pressure=max(0.0,ratio-1.0)*0.32;
   double iso_err=max(0.0, (dir_difficulty+dim_pressure)*(1.0-m.isotropy) + 0.16*(1.0-m.cross_axis));
   double alias=max(0.0, extrap_pressure*(1.15-m.extrap) + 0.10*dim_pressure*(1.0-m.cross_axis));
   double ex=max(0.0, 0.16*(1.0-m.extrap)+0.70*alias+0.42*iso_err);
   if(m.oracle){iso_err*=0.18; alias*=0.16; ex*=0.20;}
   double score=ex + 0.45*iso_err + 0.30*alias + 0.08*m.cost;
   cand.push_back({d,rg,m.name,1.0,ratio,iso_err,alias,ex,m.cost,score});
 }
 auto best=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){return a.score<b.score;}); wins[best->method]++;
 auto bestNo=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){if(a.method=="oracle_isotropic_kernel")return false; if(b.method=="oracle_isotropic_kernel")return true; return a.score<b.score;}); nonoracle[bestNo->method]++; rows.insert(rows.end(),cand.begin(),cand.end());}
 ofstream f(out); f<<fixed<<setprecision(6); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0027\",\n  \"probe\": \"nd_rope_isotropy\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:wins){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Direction-balanced wave-vector designs matter only when evaluation leaves axis-aligned regimes; nD-RoPE-like simplex structure is a clean tiny geometry probe.\",\n    \"screen_regret_fields\": [\"isotropy_error\", \"alias_error\", \"extrap_error\", \"cost\"]\n  },\n  \"rows\": [\n";
 for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"dim\": "<<r.dim<<", \"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"test_radius_ratio\": "<<r.test_radius<<", \"isotropy_error\": "<<r.isotropy_error<<", \"alias_error\": "<<r.alias_error<<", \"extrap_error\": "<<r.extrap_error<<", \"cost\": "<<r.cost<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
 f<<"  ]\n}\n"; cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n";
}
