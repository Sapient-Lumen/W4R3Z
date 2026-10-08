// CloudtainerML rev0023: native recurrent-depth screen-vs-full reversal toy, inspired by CART negative results.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <string>
#include <vector>
static std::string q(const std::string& s){ return "\"" + s + "\""; }
struct Row{std::string width,method; int prelude,loops; double screen_loss, full_loss, regret, compute, score;};
int main(int argc,char**argv){
    std::string out=argc>1?argv[1]:"REV0023_CART_SCREEN_REVERSAL_SMOKE.json";
    std::vector<int> widths={256,512,768,1024}; std::vector<int> preludes={2,4,6,8}; std::vector<int> loops={4,6,8,10,12};
    std::vector<Row> configs;
    for(int d:widths){ for(int P:preludes){ for(int R:loops){ double scale=std::log2((double)d/256.0+1.0); double full_opt=(d>=512?6.0:8.0); double screen_opt=(d>=512?8.0:6.0); double p_gain=0.055*P/(P+3.0); double full=1.0 - p_gain + 0.012*std::pow(R-full_opt,2) + 0.018*(P<6?6-P:0) + 0.00009*P*R; double screen=1.0 - 0.035*P/(P+2.0) + 0.010*std::pow(R-screen_opt,2) + 0.008*std::max(0,4-P) + 0.00003*P*R - 0.010*scale; configs.push_back({"d"+std::to_string(d),"config",P,R,screen,full,0, P*R, full}); }} }
    std::vector<std::string> policies={"stage1_screen_pick","prelude_first_prior","width_aware_loop_prior","robust_two_stage_screen","oracle_full_pick"};
    std::vector<Row> rows;
    for(int d:widths){ std::vector<Row> pool; for(auto&c:configs) if(c.width=="d"+std::to_string(d)) pool.push_back(c); auto best_full=*std::min_element(pool.begin(),pool.end(),[](const Row&a,const Row&b){return a.full_loss<b.full_loss;});
        for(auto&pol:policies){ Row pick=pool[0]; if(pol=="stage1_screen_pick") pick=*std::min_element(pool.begin(),pool.end(),[](const Row&a,const Row&b){return a.screen_loss<b.screen_loss;});
            else if(pol=="prelude_first_prior") pick=*std::min_element(pool.begin(),pool.end(),[](const Row&a,const Row&b){double sa=a.screen_loss-0.025*a.prelude+0.004*a.loops; double sb=b.screen_loss-0.025*b.prelude+0.004*b.loops; return sa<sb;});
            else if(pol=="width_aware_loop_prior") pick=*std::min_element(pool.begin(),pool.end(),[&](const Row&a,const Row&b){double opt=(d>=512?6.0:8.0); double sa=a.screen_loss+0.020*std::pow(a.loops-opt,2)-0.012*a.prelude; double sb=b.screen_loss+0.020*std::pow(b.loops-opt,2)-0.012*b.prelude; return sa<sb;});
            else if(pol=="robust_two_stage_screen") pick=*std::min_element(pool.begin(),pool.end(),[](const Row&a,const Row&b){double sa=0.6*a.screen_loss+0.4*a.full_loss+0.002*a.compute; double sb=0.6*b.screen_loss+0.4*b.full_loss+0.002*b.compute; return sa<sb;});
            else if(pol=="oracle_full_pick") pick=best_full;
            double regret=pick.full_loss-best_full.full_loss; double score=regret+0.0015*pick.compute; rows.push_back({"d"+std::to_string(d),pol,pick.prelude,pick.loops,pick.screen_loss,pick.full_loss,regret,pick.compute,score}); }
    }
    std::map<std::string,int>winners,nonoracle; size_t idx=0; for(int d:widths){(void)d; const Row*best=nullptr,*best_no=nullptr; for(size_t j=0;j<policies.size();++j){const Row&r=rows[idx++]; if(!best||r.score<best->score)best=&r; if(r.method!="oracle_full_pick"&&(!best_no||r.score<best_no->score))best_no=&r;} if(best)winners[best->method]++; if(best_no)nonoracle[best_no->method]++;}
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"cart_screen_reversal\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", ";first=false;f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", ";first=false;f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"CART-style screen/full reversals make cheap architecture sweeps dangerous: the best short-screen loop count can be anti-correlated with the full-training winner.\"\n  },\n  \"rows\": [\n";
    for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"width\": "<<q(r.width)<<", \"method\": "<<q(r.method)<<", \"prelude\": "<<r.prelude<<", \"loops\": "<<r.loops<<", \"screen_loss\": "<<r.screen_loss<<", \"full_loss\": "<<r.full_loss<<", \"regret\": "<<r.regret<<", \"compute\": "<<r.compute<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
    f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
