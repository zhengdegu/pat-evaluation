<template>
  <div class="similar-page">
    <div class="page-container">
      <div class="breadcrumb">
        <router-link to="/search">检索</router-link>
        <span class="breadcrumb__sep">›</span>
        <router-link to="/main">专利详情</router-link>
        <span class="breadcrumb__sep">›</span>
        <span>相似专利</span>
      </div>

      <div class="section-hero">
        <div class="section-hero__chip">Similar Patents</div>
        <h2 class="section-hero__title">{{ this.$store.state.patentTitle }}</h2>
        <p class="section-hero__sub">相似专利检索 · 共 {{ totalNum }} 条</p>
      </div>

      <div class="results-surface">
        <el-table :data="similarPatents" style="width: 100%" :header-cell-style="tableHeaderStyle">
          <el-table-column type="index" label="#" width="56" align="center" />
          <el-table-column prop="title" label="专利名称" min-width="300">
            <template slot-scope="scope"><span style="font-weight:500">{{ scope.row.title }}</span></template>
          </el-table-column>
          <el-table-column prop="similarity" label="相似度" width="120" align="center">
            <template slot-scope="scope"><span class="sim-chip">{{ scope.row.similarity }}</span></template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template slot-scope="scope">
              <el-button @click.native.prevent="viewDetail(scope.$index, similarPatents)" type="text" size="small">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrap">
          <el-pagination :page-size="PAGE_SIZE" :total="totalNum" @current-change="handleCurrentChange" layout="prev, pager, next" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { sprintf } from "sprintf-js";
let SIMILAR_PATENT_URL = "/api/marketfactor/similarpatents";
let GET_BASIC_INFO_URI = "/api/basicinfo/get_patent_info";

export default {
  data() { return { PAGE_SIZE: 20, similarPatents: [], totalNum: 0 }; },
  computed: {
    tableHeaderStyle() { return { background: 'var(--md-surface-container)', color: 'var(--md-on-surface-variant)', fontWeight: '600', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.06em' } }
  },
  methods: {
    reqSimlarPats(start, size) {
      axios.get(SIMILAR_PATENT_URL + "?patid=" + this.$store.state.patentId + "&start=" + start + "&size=" + size).then((response) => {
        this.totalNum = response["data"]["total"];
        let similarPatents = [];
        for (const hit of response["data"].hits) {
          similarPatents.push({ title: hit["_source"]["专利名"], similarity: sprintf("%.2f", hit["similarity"] * 100) + "%", value: hit["_source"]["转化收益（万元）"], id: hit["_source"]["申请号"], pid: hit["_source"]["专利号"] });
        }
        this.similarPatents = similarPatents;
      }).catch((error) => { console.log(error); });
    },
    handleCurrentChange(page) { this.reqSimlarPats(this.PAGE_SIZE * (page - 1), this.PAGE_SIZE); },
    viewDetail(index, data) {
      let patentId = data[index]["pid"] || data[index]["id"];
      this.$store.commit('setPatentTitle', data[index]['title']);
      this.$store.commit('setPatentId', patentId);
      this.$router.push('/main');
    }
  },
  mounted() {
    let targetPatentId = this.$route.query.patentId;
    if (targetPatentId) this.$store.commit("setPatentId", targetPatentId);
    let patentId = this.$store.state.patentId;
    if (!patentId) { this.$router.push('/search'); return; }
    axios.get(GET_BASIC_INFO_URI + "?patid=" + patentId).then((response) => {
      this.$store.commit("setPatentTitle", response["data"]["专利名"]);
    }).catch((error) => { console.log(error); });
    this.reqSimlarPats(0, this.PAGE_SIZE);
  }
};
</script>

<style scoped>
.similar-page { min-height: calc(100vh - 160px); }
.breadcrumb { font-size: 13px; color: var(--md-outline); margin-bottom: var(--space-lg); }
.breadcrumb a { color: var(--md-primary); }
.breadcrumb__sep { margin: 0 8px; color: var(--md-outline-variant); }
.section-hero { text-align: center; padding: var(--space-xl); background: var(--md-surface-container-lowest); border-radius: var(--radius-sm); box-shadow: var(--elevation-1); margin-bottom: var(--space-md); }
.section-hero__chip { display: inline-block; font-size: 11px; font-weight: 600; color: var(--md-on-primary-container); background: var(--md-primary-container); padding: 4px 14px; border-radius: var(--radius-full); letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: var(--space-sm); }
.section-hero__title { font-size: 20px; font-weight: 700; color: var(--md-on-surface); margin-bottom: 4px; }
.section-hero__sub { font-size: 14px; color: var(--md-outline); }
.results-surface { background: var(--md-surface-container-lowest); border-radius: var(--radius-sm); overflow: hidden; box-shadow: var(--elevation-1); }
.sim-chip { display: inline-block; font-size: 12px; font-weight: 600; color: var(--md-on-primary-container); background: var(--md-primary-container); padding: 3px 12px; border-radius: var(--radius-full); font-family: var(--font-mono); }
.pagination-wrap { padding: var(--space-md) 0; display: flex; justify-content: center; }
</style>
