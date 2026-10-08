// CloudtainerML rev0025: DOT-MoE-style balanced transport assignment toy for dense-to-MoE conversion.
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
struct Regime{std::string name; double cluster, anisotropy, rare, drift, capacity_pressure, router_noise;};
struct Method{std::string name; double semantic, balance, joint_route, adapt, cost, rare_protect;};
struct Row{std::string regime, method; int experts; double active_fraction, retention, imbalance, route_miss, wall_proxy, score;};
int main(int argc,char**argv){
  std::string out=argc>1?argv[1]:"REV0025_DOT_MOE_TRANSPORT_SMOKE.json";
  std::vector<Regime> regimes={{"clean_semantic_clusters",0.92,0.20,0.06,0.04,0.35,0.10},{"overlapping_neuron_functions",0.44,0.72,0.12,0.10,0.55,0.22},{"rare_specialist_neurons",0.70,0.30,0.86,0.12,0.72,0.18},{"router_distribution_shift",0.68,0.28,0.18,0.88,0.62,0.30},{"capacity_bottleneck",0.75,0.40,0.25,0.20,0.96,0.18},{"anisotropic_dense_layer",0.55,0.95,0.20,0.15,0.58,0.25}};
  std::vector<Method> methods={{"structured_pruning",0.12,0.20,0.00,0.00,0.03,0.05},{"random_split_moe",0.05,0.88,0.05,0.08,0.04,0.10},{"kmeans_neuron_cluster",0.65,0.28,0.10,0.10,0.07,0.12},{"balanced_greedy_cluster",0.55,0.78,0.14,0.16,0.08,0.30},{"dot_sinkhorn_balanced",0.75,0.92,0.35,0.30,0.16,0.40},{"dot_plus_joint_router",0.78,0.86,0.72,0.62,0.23,0.55},{"oracle_assignment",1.00,1.00,1.00,1.00,0.30,1.00}};
  std::vector<int> experts={4,8,16,32}; std::vector<double> active={0.50,0.35,0.25};
  std::vector<Row> rows;
  for(const auto& rg:regimes){ for(int E:experts){ for(double af:active){ double cap=std::min(1.0,std::log2((double)E)/5.0); for(const auto&m:methods){
    double semantic_fit=rg.cluster*(0.10+0.78*m.semantic)*(0.75+0.25*cap);
    double anisotropy_loss=rg.anisotropy*(0.38*(1.0-m.semantic)+0.22*(1.0-m.balance));
    double capacity_loss=rg.capacity_pressure*(0.45*(1.0-m.balance)+0.28*std::max(0.0,0.45-af));
    double rare_loss=rg.rare*(0.48*(1.0-m.rare_protect)+0.18*(1.0-m.joint_route));
    double drift_loss=rg.drift*(0.38*(1.0-m.adapt)+0.16*(1.0-m.joint_route));
    double route_miss=std::max(0.0,std::min(1.0, rg.router_noise*(0.7-0.45*m.joint_route)+rg.drift*(0.45-0.30*m.adapt)+rg.rare*(0.20-0.12*m.rare_protect)));
    double retention=std::max(0.0,std::min(1.08, 0.52+0.42*semantic_fit + 0.22*m.joint_route + 0.10*m.balance - anisotropy_loss - rare_loss - drift_loss - 0.50*route_miss));
    if(m.name=="oracle_assignment") retention=std::min(1.0,0.94+0.04*cap-0.04*rg.capacity_pressure);
    double imbalance=std::max(0.0,std::min(1.0, rg.capacity_pressure*(1.0-m.balance)*(0.55+0.12*std::log2((double)E)) + 0.15*(1.0-af)));
    double wall=1.0 - 0.62*(1.0-af)*(0.8+0.2*m.balance) + 0.10*m.cost + 0.08*imbalance + 0.04*std::log2((double)E);
    double score=(1.0-retention) + 0.26*route_miss + 0.18*imbalance + 0.08*std::max(0.0,wall-0.72);
    rows.push_back({rg.name,m.name,E,af,retention,imbalance,route_miss,wall,score});
  }}}}
  std::map<std::string,int> winners, nonoracle; size_t idx=0; for(auto& rg:regimes){(void)rg; for(int E:experts){(void)E; for(double af:active){(void)af; const Row*best=nullptr; const Row*bestNo=nullptr; for(size_t j=0;j<methods.size();++j){const Row&r=rows[idx++]; if(!best||r.score<best->score)best=&r; if(r.method!="oracle_assignment"&&(!bestNo||r.score<bestNo->score))bestNo=&r;} if(best)winners[best->method]++; if(bestNo)nonoracle[bestNo->method]++; }} }
  std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
  f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0025\",\n  \"probe\": \"dot_moe_transport_assignment\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Balanced transport is only interesting when semantic grouping, capacity constraints, and route consistency are all active; random split and plain clustering are strong enough in some clean regimes that DOT-style machinery needs rare/drift/load traps to earn its cost.\"\n  },\n  \"rows\": [\n";
  for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"experts\": "<<r.experts<<", \"active_fraction\": "<<r.active_fraction<<", \"retention\": "<<r.retention<<", \"imbalance\": "<<r.imbalance<<", \"route_miss\": "<<r.route_miss<<", \"wall_proxy\": "<<r.wall_proxy<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
  f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
