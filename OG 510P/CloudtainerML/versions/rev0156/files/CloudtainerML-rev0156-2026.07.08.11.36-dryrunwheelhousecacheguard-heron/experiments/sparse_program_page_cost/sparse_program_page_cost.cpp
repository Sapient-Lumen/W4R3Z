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
struct Program{std::string name; double density; double dynamic; double page_align; double fusion; double exact; double selector_quality;};
int main(){
  std::string rev="rev0036", revup="REV0036";
  std::vector<Program> ps={
    {"dense_contiguous",1.00,0.00,1.00,0.85,1.00,1.00},
    {"static_block_sparse",0.30,0.05,0.95,0.70,0.74,0.70},
    {"dynamic_token_topk",0.16,0.90,0.30,0.20,0.88,0.86},
    {"page_aligned_block_topk",0.22,0.45,0.90,0.62,0.84,0.82},
    {"vflow_fused_program",0.20,0.34,0.92,0.88,0.86,0.84},
    {"boundary_bridge_page_program",0.24,0.28,0.84,0.78,0.90,0.80},
    {"oracle_sparse_pages",0.14,0.15,1.00,0.95,0.98,1.00}
  };
  std::vector<int> lengths={1024,4096,16384,65536};
  std::vector<int> page_sizes={16,32,64,128};
  std::ostringstream rows; bool first=true; int n=0; std::map<std::string,int> wins;
  for(int L: lengths){ for(int P: page_sizes){ for(double generation: {0.25,0.60,1.0}){
    double best=1e99; std::string winner;
    struct R{std::string name; double traffic,selector,kernel,wall,acc,score; bool exact_miss;}; std::vector<R> rr;
    for(auto &p: ps){
      double pages=std::ceil((double)L/P);
      double traffic = p.density * pages * (0.65 + 0.35*generation);
      double selector = p.dynamic * pages * 0.045 * (1.0 + 0.8*generation);
      double misalign = (1.0-p.page_align) * pages * 0.018;
      double kernel = (1.0-p.fusion) * (2.0 + 0.015*pages) + misalign;
      double exact_pen = std::max(0.0, 0.88-p.exact) * (0.8+0.5*generation);
      bool miss = p.exact < 0.80 && L>=16384;
      double wall = traffic + selector + kernel + exact_pen*pages*0.03;
      double acc = p.exact * (0.92 + 0.08*p.selector_quality) - (miss?0.08:0.0);
      double score = wall + 80.0*std::max(0.0,0.88-acc); // lower is better
      rr.push_back({p.name,traffic,selector,kernel,wall,acc,score,miss});
      if(p.name!="oracle_sparse_pages" && score<best){best=score; winner=p.name;}
    }
    wins[winner]++;
    for(auto &r: rr){if(!first) rows<<",\n"; first=false; n++; rows<<"    {\"seq_len\":"<<L<<",\"page_size\":"<<P<<",\"generation_frac\":"<<generation<<",\"program\":\""<<esc(r.name)<<"\",\"winner_excluding_oracle\":\""<<esc(winner)<<"\",\"traffic_proxy\":"<<r.traffic<<",\"selector_overhead\":"<<r.selector<<",\"kernel_penalty\":"<<r.kernel<<",\"wall_proxy\":"<<r.wall<<",\"accuracy_proxy\":"<<r.acc<<",\"exact_miss\":"<<(r.exact_miss?"true":"false")<<",\"score\":"<<r.score<<"}";}
  }}}
  std::string top=""; int wc=-1; for(auto &kv:wins){if(kv.second>wc){wc=kv.second; top=kv.first;}}
  std::ofstream f("artifacts/probe-results/"+revup+"_SPARSE_PROGRAM_PAGE_COST_SMOKE.json");
  f<<std::setprecision(6)<<"{\n  \"project\":\"CloudtainerML\",\n  \"revision\":\""<<rev<<"\",\n  \"probe\":\"sparse_program_page_cost\",\n  \"kind\":\"native_cxx_probe\",\n  \"source_ids\":[\"SRC-0355\"],\n  \"cell_ids\":[\"CELL-343\"],\n  \"summary\":{\n    \"primary_metric\":{\"name\":\"score\",\"direction\":\"lower_is_better\"},\n    \"top_non_oracle_winner\":\""<<esc(top)<<"\",\n    \"winner_count\":"<<wc<<",\n    \"guard_fields\":[\"wall_proxy\",\"selector_overhead\",\"kernel_penalty\",\"exact_miss\"],\n    \"interpretation\":\"Sparse attention program quality depends on page alignment, selector overhead, and fusion, not just nominal density; dynamic token top-k can lose to page-aligned fused programs.\"\n  },\n  \"rows\":[\n"<<rows.str()<<"\n  ]\n}\n";
  std::cout<<"{\"top_non_oracle_winner\":\""<<esc(top)<<"\",\"rows\":"<<n<<"}\n";
}
