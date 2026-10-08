// CloudtainerML rev0024: native tensor-vs-matrix decomposition sanity probe.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <string>
#include <vector>
static std::string q(const std::string&s){return "\""+s+"\"";}
struct Regime{std::string name; double shared_subspace, heterogeneity, outliers, repairable, tensor_order;};
struct Method{std::string name; double shared_assumption, component_awareness, repair, overhead, tensor_bias;};
struct Row{std::string regime, method; double keep_frac, recon_error, downstream_loss, overhead, score;};
int main(int argc,char**argv){
 std::string out=argc>1?argv[1]:"REV0024_TENSOR_MATRIX_DECOMP_SANITY_SMOKE.json";
 std::vector<Regime> regimes={{"shared_head_subspace",0.88,0.12,0.08,0.30,0.70},{"heterogeneous_attention_heads",0.22,0.86,0.20,0.35,0.55},{"moe_expert_heterogeneity",0.18,0.92,0.25,0.48,0.78},{"smooth_mlp_block",0.72,0.25,0.12,0.65,0.35},{"superweight_outlier",0.30,0.55,0.90,0.72,0.40},{"calibration_repair_friendly",0.50,0.45,0.40,0.92,0.48}};
 std::vector<Method> methods={{"matrix_svd_layerwise",0.20,0.74,0.00,0.05,0.00},{"componentwise_svd_qk_ov_mlp",0.18,0.90,0.00,0.11,0.00},{"tucker_tensor_shared",0.82,0.36,0.00,0.10,0.85},{"tensor_train_shared",0.78,0.32,0.00,0.14,0.90},{"tensor_plus_lora_repair",0.76,0.45,0.70,0.24,0.82},{"matrix_plus_outlier_restore",0.20,0.82,0.55,0.16,0.00},{"oracle_component_budget",0.10,1.00,1.00,0.28,0.00}};
 std::vector<double> keeps={0.15,0.25,0.40,0.60,0.80}; std::vector<Row> rows;
 for(auto&rg:regimes){for(double k:keeps){double comp=1.0-k; for(auto&m:methods){
   double capacity=std::sqrt(k)*(0.60+0.40*m.component_awareness);
   double mismatch=rg.heterogeneity*m.shared_assumption*(0.55+0.30*rg.tensor_order) + (1.0-rg.shared_subspace)*m.tensor_bias*0.30;
   double outlier_loss=rg.outliers*(0.42*(1.0-m.repair)+0.10*(1.0-m.component_awareness));
   double repair_gain=rg.repairable*m.repair*0.38;
   double tensor_gain=rg.shared_subspace*m.tensor_bias*0.30;
   double recon=std::max(0.01, 1.05 - capacity - tensor_gain + mismatch + outlier_loss - repair_gain + 0.18*comp);
   if(m.name=="oracle_component_budget") recon=std::max(0.005, recon*0.45-0.03*rg.repairable);
   double downstream = recon*(0.70+0.45*rg.heterogeneity+0.25*rg.outliers) + 0.04*m.overhead;
   double overhead=m.overhead + 0.12*m.repair + 0.10*m.tensor_bias;
   double score=downstream+0.12*overhead+0.04*(1.0-k);
   rows.push_back({rg.name,m.name,k,recon,downstream,overhead,score});
 }} }
 std::map<std::string,int>winners,nonoracle; size_t idx=0; for(auto&rg:regimes){(void)rg; for(double k:keeps){(void)k; const Row*best=nullptr; const Row*bestNo=nullptr; for(size_t j=0;j<methods.size();++j){const Row&r=rows[idx++]; if(!best||r.score<best->score)best=&r; if(r.method!="oracle_component_budget"&&(!bestNo||r.score<bestNo->score))bestNo=&r;} if(best)winners[best->method]++; if(bestNo)nonoracle[bestNo->method]++;}}
 std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
 f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0024\",\n  \"probe\": \"tensor_matrix_decomp_sanity\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Tensor decompositions only win in genuinely shared-subspace regimes; componentwise matrix methods and outlier/repair paths are safer when heads or experts are heterogeneous.\"\n  },\n  \"rows\": [\n";
 for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"keep_frac\": "<<r.keep_frac<<", \"recon_error\": "<<r.recon_error<<", \"downstream_loss\": "<<r.downstream_loss<<", \"overhead\": "<<r.overhead<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
 f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0; }
