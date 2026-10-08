// CloudtainerML rev0023: native safety-tail phase/HPO wind tunnel.
// Synthetic C++17 probe. It tries to find configurations where mean task error
// stays tolerable while a hidden safety/alignment subspace catastrophically flips.
// Not a paper reproduction.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <sstream>
#include <string>
#include <vector>

struct Config{int bits; int gran; double outlier; double safety; int protected_dims;};
struct Row{std::string regime,policy; int budget=0,n=0; double risk_found=0,best_tail=0,best_hidden=0,mean_task=0,query_cost=0,utility=0;};
static std::string esc(const std::string&s){std::string o; for(char c:s){if(c=='"')o+="\\\""; else if(c=='\\')o+="\\\\"; else o+=c;} return o;}
static double clamp(double x,double a,double b){return std::max(a,std::min(b,x));}
static double rnd(std::mt19937_64&r,double a=0,double b=1){return std::uniform_real_distribution<double>(a,b)(r);} 
struct Eval{double task_err, safety_flip, tail, hidden_risk; bool failure;};
static Eval eval_config(const std::string&reg,const Config&c,int seed){
    std::mt19937_64 rng(seed + c.bits*1009 + c.gran*37 + int(c.outlier*31) + int(c.safety*91));
    double gran_bonus = c.gran<=1 ? 0.75 : c.gran<=4 ? 0.90 : 1.08;
    double protect = 1.0 - 0.055*c.protected_dims;
    protect = clamp(protect,0.32,1.0);
    double lowbit = std::pow(2.0, std::max(0,5-c.bits))*0.042;
    double out = c.outlier*0.018;
    double safety_noise = lowbit * gran_bonus * protect * (0.65 + 0.35*c.safety) + out*(c.gran>=8?1.0:0.55);
    double task_noise = lowbit*(0.65+0.12*c.outlier)/(1.0+0.05*c.protected_dims);
    if(reg=="outlier_crush") safety_noise*=1.65;
    if(reg=="safety_is_outlier") { safety_noise*= (c.gran<=1?1.35:0.90); task_noise*=1.08; }
    if(reg=="multi_layer_dilution") { safety_noise*=1.22+0.10*std::sin(seed); task_noise*=0.85; }
    if(reg=="benign") { safety_noise*=0.45; task_noise*=0.55; }
    if(reg=="phase_cliff") { double cliff=(c.bits<=3 && c.outlier>7.0 && c.protected_dims<4)?2.2:0.75; safety_noise*=cliff; }
    double jitter=0.8+0.4*rnd(rng);
    double tail = safety_noise*jitter + 0.02*rnd(rng);
    double flip = 1.0/(1.0+std::exp(-(tail-0.28)*9.0));
    double task = task_noise*(0.75+0.5*rnd(rng));
    bool failure = (flip>0.38 && task<0.58) || tail>0.55;
    double hidden = 3.5*flip + 1.7*tail - 0.55*task;
    return {task,flip,tail,hidden,failure};
}
static Config random_cfg(std::mt19937_64&rng){return {int(2+rng()%7), int((int[]){1,2,4,8,16}[rng()%5]), rnd(rng,1,11), rnd(rng,0.2,1.6), int(rng()%13)};}
static Config domain_cfg(std::mt19937_64&rng){int bits=(rng()%100<70)?int(2+rng()%3):int(5+rng()%4); int gran=(rng()%100<60)?8:((int[]){1,2,4,16}[rng()%4]); return {bits,gran,rnd(rng,5.0,11.5),rnd(rng,0.55,1.7),int(rng()%7)};}
static Config grid_cfg(int i){int bits[]={2,3,4,6,8}; int gran[]={1,4,8,16}; double out[]={2,5,8,11}; double saf[]={0.35,0.75,1.15,1.55}; int prot[]={0,2,6,10}; int x=i; Config c; c.bits=bits[x%5]; x/=5; c.gran=gran[x%4]; x/=4; c.outlier=out[x%4]; x/=4; c.safety=saf[x%4]; x/=4; c.protected_dims=prot[x%4]; return c;}
static Config centaur_cfg(std::mt19937_64&rng,const std::vector<Config>&good){ if(good.empty()||rng()%100<35) return domain_cfg(rng); const Config&g=good[rng()%good.size()]; Config c=g; if(rng()%2)c.bits=std::max(2,std::min(8,c.bits+int(rng()%3)-1)); if(rng()%2)c.gran=((int[]){1,2,4,8,16}[rng()%5]); c.outlier=clamp(c.outlier+rnd(rng,-1.5,1.5),1,12); c.safety=clamp(c.safety+rnd(rng,-0.25,0.25),0.1,2.0); c.protected_dims=std::max(0,std::min(12,c.protected_dims+int(rng()%5)-2)); return c; }
static void add(Row&r,double risk,double tail,double hidden,double task,double cost,double util){r.n++; r.risk_found+=risk; r.best_tail+=tail; r.best_hidden+=hidden; r.mean_task+=task; r.query_cost+=cost; r.utility+=util;}
int main(int argc,char**argv){
    std::string out="artifacts/probe-results/REV0023_SAFETY_TAIL_PHASE_SMOKE.json"; if(argc>1) out=argv[1];
    auto t0=std::chrono::high_resolution_clock::now();
    std::vector<std::string> regimes={"outlier_crush","safety_is_outlier","multi_layer_dilution","phase_cliff","benign"};
    std::vector<std::string> policies={"grid","random","domain_prior","centaur_state_prior"};
    std::vector<int> budgets={16,32,64,128};
    std::map<std::string,Row> rows; std::map<std::string,int> wins;
    for(auto&reg:regimes) for(int budget:budgets) for(int seed=0;seed<80;++seed){
        double best_util=-1e9; std::string best_policy;
        for(auto&pol:policies){std::mt19937_64 rng(9001+seed*17+budget*19+reg.size()*23+pol.size()); std::vector<Config> good; bool found=false; double best_tail=0,best_hidden=-1e9,task_at=0; double cost=0;
            for(int i=0;i<budget;++i){Config c; if(pol=="grid") c=grid_cfg(i); else if(pol=="random") c=random_cfg(rng); else if(pol=="domain_prior") c=domain_cfg(rng); else c=centaur_cfg(rng,good); Eval e=eval_config(reg,c,seed*1000+i); cost += (pol=="centaur_state_prior"?1.28:pol=="domain_prior"?1.08:1.0); if(e.failure){found=true; good.push_back(c);} if(e.tail>best_tail){best_tail=e.tail; task_at=e.task_err;} if(e.hidden_risk>best_hidden) best_hidden=e.hidden_risk; }
            double util=(found?3.0:0.0)+1.5*best_tail+0.55*best_hidden-0.012*cost-0.2*task_at; std::string key=reg+"|"+std::to_string(budget)+"|"+pol; if(!rows.count(key)){rows[key].regime=reg; rows[key].budget=budget; rows[key].policy=pol;} add(rows[key],found?1:0,best_tail,best_hidden,task_at,cost,util); if(util>best_util){best_util=util; best_policy=pol;}}
        wins[best_policy]++; }
    double seconds=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count();
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"safety_tail_phase\",\n  \"language\": \"c++17\",\n  \"is_paper_reproduction\": false,\n";
    f<<"  \"taxonomy\": [\"lossy-cache\", \"quantization\", \"safety-tail\", \"hpo\", \"phase-diagram\"],\n";
    f<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<seconds<<", \"primary_metric\": {\"name\": \"mean_utility\", \"direction\": \"higher_is_better\", \"winner_field\": \"winner_counts\"}, \"tail_metrics\": {\"has_catastrophic_proxy\": true, \"fields\": [\"risk_found_rate\", \"mean_best_tail\", \"mean_best_hidden_risk\"]}, \"winner_counts\": {"; bool first=true; for(auto&kv:wins){if(!first)f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second;} f<<"}, \"interpretation\": \"Search policy toy for finding hidden safety-tail phase transitions under low-bit cache quantization; not a model-level validation.\"},\n  \"rows\": [\n";
    int c=0; for(auto&kv:rows){const Row&r=kv.second; double n=std::max(1,r.n); if(c++)f<<",\n"; f<<"    {\"regime\": \""<<esc(r.regime)<<"\", \"budget\": "<<r.budget<<", \"policy\": \""<<esc(r.policy)<<"\", \"risk_found_rate\": "<<r.risk_found/n<<", \"mean_best_tail\": "<<r.best_tail/n<<", \"mean_best_hidden_risk\": "<<r.best_hidden/n<<", \"mean_task_error_at_best_tail\": "<<r.mean_task/n<<", \"mean_query_cost\": "<<r.query_cost/n<<", \"mean_utility\": "<<r.utility/n<<"}";}
    f<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0; }
