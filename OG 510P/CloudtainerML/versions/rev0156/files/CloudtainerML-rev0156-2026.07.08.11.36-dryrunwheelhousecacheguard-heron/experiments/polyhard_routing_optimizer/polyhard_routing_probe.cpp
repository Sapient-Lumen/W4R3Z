// CloudtainerML rev0025: PolyStep-inspired forward-only optimizer toy for hard routers/argmax choices.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <string>
#include <vector>
static std::string q(const std::string&s){return "\""+s+"\"";}
struct Regime{std::string name; double discreteness, noise, dimension, basin, eval_budget, trap;};
struct Method{std::string name; double subspace, vertices, temperature, exploration, geometry, overhead;};
struct Row{std::string regime, method; int budget; double best_loss, stability, query_cost, score;};
int main(int argc,char**argv){
  std::string out=argc>1?argv[1]:"REV0025_POLYHARD_ROUTING_SMOKE.json";
  std::vector<Regime> regimes={{"hard_moe_clean",0.90,0.10,0.40,0.75,0.60,0.20},{"argmax_attention_plateaus",0.96,0.18,0.55,0.38,0.60,0.55},{"int8_quantized_router",0.82,0.35,0.62,0.45,0.45,0.42},{"high_dimensional_hard_gate",0.88,0.25,0.95,0.34,0.40,0.60},{"noisy_forward_eval",0.75,0.92,0.55,0.52,0.55,0.45},{"smooth_surrogate_friendly",0.30,0.18,0.42,0.70,0.70,0.18}};
  std::vector<Method> methods={{"random_search",0.05,0.20,0.30,0.88,0.05,0.04},{"evolution_strategy",0.28,0.45,0.45,0.70,0.22,0.10},{"straight_through_surrogate",0.55,0.30,0.60,0.25,0.20,0.08},{"coordinate_hillclimb",0.25,0.25,0.20,0.32,0.30,0.05},{"polystep_like_subspace",0.78,0.78,0.72,0.62,0.82,0.20},{"polystep_low_budget",0.68,0.55,0.68,0.50,0.70,0.12},{"oracle_forward_optimizer",1.00,1.00,1.00,1.00,1.00,0.28}};
  std::vector<int> budgets={32,64,128,256}; std::vector<Row> rows;
  for(auto&rg:regimes){for(int B:budgets){double bscale=std::min(1.0,std::log2((double)B/16.0)/4.0); for(auto&m:methods){
    double plateau_gain=rg.discreteness*(0.15+0.45*m.geometry+0.18*m.vertices)*(0.60+0.40*bscale);
    double basin_gain=rg.basin*(0.20+0.35*m.exploration+0.25*m.subspace);
    double smooth_gain=(1.0-rg.discreteness)*(0.35+0.45*(m.name=="straight_through_surrogate"));
    double dim_pen=rg.dimension*(0.34*(1.0-m.subspace)+0.16*(1.0-bscale));
    double noise_pen=rg.noise*(0.28*(1.0-m.temperature)+0.18*m.vertices+0.12*m.overhead);
    double trap_pen=rg.trap*(0.42*(1.0-m.exploration)+0.18*(1.0-m.geometry));
    double loss=std::max(0.02,1.12-plateau_gain-basin_gain-smooth_gain+dim_pen+noise_pen+trap_pen);
    if(m.name=="oracle_forward_optimizer") loss=std::max(0.01,loss*0.45-0.08*bscale);
    double stability=std::max(0.0,std::min(1.0,0.55+0.30*m.temperature+0.22*m.geometry-0.28*rg.noise-0.14*rg.trap));
    double qcost=(B/64.0)*(1.0+0.55*m.overhead+0.15*m.vertices);
    double score=loss+0.16*(1.0-stability)+0.035*qcost;
    rows.push_back({rg.name,m.name,B,loss,stability,qcost,score});
  }}}
  std::map<std::string,int>winners,nonoracle; size_t idx=0; for(auto&rg:regimes){(void)rg; for(int B:budgets){(void)B; const Row*best=nullptr; const Row*bestNo=nullptr; for(size_t j=0;j<methods.size();++j){const Row&r=rows[idx++]; if(!best||r.score<best->score)best=&r; if(r.method!="oracle_forward_optimizer"&&(!bestNo||r.score<bestNo->score))bestNo=&r;} if(best)winners[best->method]++; if(bestNo)nonoracle[bestNo->method]++; }}
  std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
  f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0025\",\n  \"probe\": \"polyhard_routing_optimizer\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Forward-only PolyStep-like geometry is worth testing for hard routing only when plateaus/discreteness dominate; surrogate gradients remain competitive in smooth regimes and noisy forward evaluation can erase the advantage.\"\n  },\n  \"rows\": [\n";
  for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"budget\": "<<r.budget<<", \"best_loss\": "<<r.best_loss<<", \"stability\": "<<r.stability<<", \"query_cost\": "<<r.query_cost<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
  f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0; }
