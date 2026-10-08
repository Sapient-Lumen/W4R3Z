#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>
static std::string esc(const std::string& s){std::string o; for(char c:s){if(c=='"'||c=='\\') o+='\\'; o+=c;} return o;}
static double clamp(double x,double lo,double hi){return std::max(lo,std::min(hi,x));}
struct Regime{std::string name; double content_dep; double recency_dep; double deep_dep; double confound;};
struct Probe{std::string name; double content_sens; double recency_bias; double depth_select; double ablation_faith; double cost;};
int main(){
  std::string rev="rev0036", revup="REV0036";
  std::vector<Regime> regs={{"recency_task",0.10,0.92,0.20,0.10},{"content_switch",0.88,0.25,0.35,0.20},{"deep_feature_task",0.55,0.20,0.90,0.25},{"wrapped_schedule_trap",0.80,0.80,0.60,0.85},{"confounded_probe",0.65,0.60,0.65,0.70}};
  std::vector<Probe> probes={{"posthoc_recency_schedule",0.05,0.95,0.30,0.25,0.10},{"additive_residual_patch_probe",0.35,0.40,0.35,0.55,0.35},{"learned_content_depth_route",0.82,0.35,0.74,0.74,0.65},{"causal_ablation_route_probe",0.65,0.45,0.68,0.88,0.85},{"oracle_mechanism_route",1.00,1.00,1.00,1.00,1.15}};
  std::ostringstream rows; bool first=true; int n=0; std::map<std::string,int>wins;
  for(auto&r:regs){for(double budget:{0.35,0.70,1.00}){
    double best=-1e9; std::string winner; struct Row{std::string m; double content,causal,confound,score,cost; bool over;}; std::vector<Row> rr;
    for(auto&p:probes){
      bool over=p.cost>budget;
      double content_match=1.0-std::abs(r.content_dep-p.content_sens);
      double rec_match=1.0-std::abs(r.recency_dep-p.recency_bias);
      double depth_match=1.0-std::abs(r.deep_dep-p.depth_select);
      double causal=p.ablation_faith*(0.6+0.4*r.content_dep);
      double confound_pen=r.confound*(p.recency_bias*0.45 + (1.0-p.ablation_faith)*0.55);
      double interpretability=0.36*content_match+0.22*rec_match+0.25*depth_match+0.35*causal-confound_pen-0.05*p.cost-(over?0.35:0.0);
      rr.push_back({p.name,content_match,causal,confound_pen,interpretability,p.cost,over});
      if(p.name!="oracle_mechanism_route"&&interpretability>best){best=interpretability;winner=p.name;}
    }
    wins[winner]++;
    for(auto&x:rr){if(!first)rows<<",\n";first=false;n++;rows<<"    {\"regime\":\""<<esc(r.name)<<"\",\"budget\":"<<budget<<",\"method\":\""<<esc(x.m)<<"\",\"winner_excluding_oracle\":\""<<esc(winner)<<"\",\"content_match\":"<<x.content<<",\"causal_ablation_match\":"<<x.causal<<",\"confound_penalty\":"<<x.confound<<",\"realized_cost\":"<<x.cost<<",\"budget_over\":"<<(x.over?"true":"false")<<",\"score\":"<<x.score<<"}";}
  }}
  std::string top="";int wc=-1;for(auto&kv:wins){if(kv.second>wc){wc=kv.second;top=kv.first;}}
  std::ofstream f("artifacts/probe-results/"+revup+"_DEPTH_ROUTE_INTERPRETABILITY_SMOKE.json");
  f<<std::setprecision(6)<<"{\n  \"project\":\"CloudtainerML\",\n  \"revision\":\""<<rev<<"\",\n  \"probe\":\"depth_route_interpretability\",\n  \"kind\":\"native_cxx_probe\",\n  \"source_ids\":[\"SRC-0356\"],\n  \"cell_ids\":[\"CELL-344\"],\n  \"summary\":{\n    \"primary_metric\":{\"name\":\"score\",\"direction\":\"higher_is_better\"},\n    \"top_non_oracle_winner\":\""<<esc(top)<<"\",\n    \"winner_count\":"<<wc<<",\n    \"guard_fields\":[\"content_match\",\"causal_ablation_match\",\"confound_penalty\",\"budget_over\"],\n    \"interpretation\":\"Exposed depth-routing weights are not automatically interpretable: posthoc recency schedules can look clean while failing content-dependent causal probes.\"\n  },\n  \"rows\":[\n"<<rows.str()<<"\n  ]\n}\n";
  std::cout<<"{\"top_non_oracle_winner\":\""<<esc(top)<<"\",\"rows\":"<<n<<"}\n";
}
