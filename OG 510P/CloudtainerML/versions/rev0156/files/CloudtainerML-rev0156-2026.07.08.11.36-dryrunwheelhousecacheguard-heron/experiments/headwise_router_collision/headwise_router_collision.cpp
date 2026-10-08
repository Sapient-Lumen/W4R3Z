// CloudtainerML rev0028 — Head-wise MoE router collision wind tunnel.
// Inspired by work arguing multi-head attention can cause route-collision bottlenecks in MoE Transformers.
#include <bits/stdc++.h>
using namespace std; static string q(const string&s){string o="\""; for(char c:s){if(c=='"'||c=='\\')o+='\\'; o+=c;} return o+'"';}
struct Regime{string name; double factors, head_separability, cooccurrence, task_drift, load, noise;};
struct Method{string name; double granularity, headwise, balance, adapt, overhead; bool oracle=false;};
struct Row{string regime, method; int heads; double route_collision, old_loss_proxy, load_violation, wall_proxy, score;};
int main(int argc,char**argv){string out=argc>1?argv[1]:"REV0028_HEADWISE_ROUTER_COLLISION_SMOKE.json";
 vector<Regime> regs={{"single_factor_easy",0.20,0.72,0.18,0.08,0.25,0.10},{"cooccurring_semantic_structural",0.88,0.78,0.92,0.42,0.36,0.14},{"low_head_separability",0.80,0.22,0.80,0.36,0.42,0.18},{"continual_drift",0.72,0.68,0.72,0.90,0.44,0.22},{"load_pressure_many_heads",0.70,0.62,0.70,0.30,0.92,0.16},{"noisy_head_features",0.66,0.54,0.68,0.42,0.38,0.84}};
 vector<Method> ms={{"concat_router",0.28,0.00,0.42,0.16,0.00,false},{"concat_plus_load_aux",0.32,0.00,0.78,0.22,0.05,false},{"headwise_router",0.74,0.82,0.50,0.48,0.14,false},{"headwise_balance_repair",0.68,0.78,0.84,0.50,0.19,false},{"factorized_product_router",0.82,0.64,0.58,0.56,0.24,false},{"oracle_factor_router",1.00,1.00,1.00,1.00,0.30,true}};
 vector<int> H={4,8,16}; vector<Row> rows; map<string,int>winners,nonoracle;
 for(auto&rg:regs)for(int h:H){vector<Row> cand; double hbonus=min(1.0,log2((double)h)/4.0); for(auto&m:ms){
   double collision=max(0.0,rg.factors*rg.cooccurrence*(0.78*(1-m.granularity)+0.35*(1-m.headwise*rg.head_separability))-0.08*hbonus*m.headwise);
   double drift_loss=rg.task_drift*(0.42*collision+0.22*(1-m.adapt));
   double load=max(0.0,rg.load*(0.55*(1-m.balance)+0.10*hbonus));
   double noise=rg.noise*(0.20*m.headwise*(1-rg.head_separability)+0.10*(1-m.adapt));
   double oldloss=0.18+0.72*collision+0.36*drift_loss+0.18*noise;
   double wall=0.30+0.06*hbonus+0.22*m.overhead;
   if(m.oracle){collision=0.03*rg.factors; oldloss=0.06+0.02*rg.noise; load=0.03*rg.load; wall=0.42;}
   double score=oldloss+0.22*load+0.10*wall;
   cand.push_back({rg.name,m.name,h,collision,oldloss,load,wall,score});}
 auto best=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){return a.score<b.score;}); winners[best->method]++;
 auto bestNo=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){if(a.method=="oracle_factor_router")return false;if(b.method=="oracle_factor_router")return true;return a.score<b.score;}); nonoracle[bestNo->method]++; rows.insert(rows.end(),cand.begin(),cand.end());}
 ofstream f(out); f<<fixed<<setprecision(6); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0028\",\n  \"probe\": \"headwise_router_collision\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Head-wise routing is only justified when head channels contain separable factors; otherwise it adds overhead or noise without reducing route collisions.\",\n    \"screen_regret_fields\": [\"route_collision\", \"old_loss_proxy\", \"load_violation\", \"wall_proxy\"]\n  },\n  \"rows\": [\n";
 for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"heads\": "<<r.heads<<", \"route_collision\": "<<r.route_collision<<", \"old_loss_proxy\": "<<r.old_loss_proxy<<", \"load_violation\": "<<r.load_violation<<", \"wall_proxy\": "<<r.wall_proxy<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
 f<<"  ]\n}\n"; cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n";}
