<template>
  <div class="tech-detail">
    <title-canvas title="适用范围">
      <div class="ipc-tags">
        <span class="ipc-tag" v-for="(ipc, idx) in applicabilities" :key="idx">{{ ipc }}</span>
        <span v-if="!applicabilities.length" class="text-tertiary">暂无数据</span>
      </div>
    </title-canvas>

    <title-canvas title="专利申请人论文">
      <el-table :data="authorThesises" style="width:100%" :header-cell-style="tableHeaderStyle">
        <el-table-column type="index" label="#" width="56" align="center" />
        <el-table-column prop="title" label="论文题目" min-width="300">
          <template slot-scope="scope">
            <span style="font-weight:500">{{ scope.row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="200" />
        <el-table-column prop="referenceNum" label="引用次数" width="100" align="center">
          <template slot-scope="scope">
            <span class="text-mono">{{ scope.row.referenceNum }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="similarity" label="相似度" width="100" align="center">
          <template slot-scope="scope">
            <span class="badge-value">{{ scope.row.similarity }}</span>
          </template>
        </el-table-column>
      </el-table>
    </title-canvas>

    <title-canvas title="其他相关论文">
      <el-table :data="otherThesises" style="width:100%" :header-cell-style="tableHeaderStyle">
        <el-table-column type="index" label="#" width="56" align="center" />
        <el-table-column prop="author" label="作者" width="160" />
        <el-table-column prop="title" label="论文题目" min-width="300">
          <template slot-scope="scope">
            <span style="font-weight:500">{{ scope.row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="200" />
        <el-table-column prop="referenceNum" label="引用次数" width="100" align="center">
          <template slot-scope="scope">
            <span class="text-mono">{{ scope.row.referenceNum }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="similarity" label="相似度" width="100" align="center">
          <template slot-scope="scope">
            <span class="badge-value">{{ scope.row.similarity }}</span>
          </template>
        </el-table-column>
      </el-table>
    </title-canvas>
  </div>
</template>

<script>
import axios from "axios";

let APPLICABILITY_URL = '/api/techfactor/applicability';
let THESISBYAPPLICANT_URL = '/api/techfactor/thesisbyapplicant';
let SIMILARTHESIS_URL = '/api/techfactor/similarthesis';

export default {
  data() {
    return {
      applicabilities: [],
      authorThesises: [],
      otherThesises: []
    };
  },
  computed: {
    tableHeaderStyle() {
      return {
        background: '#f8f9fb', color: '#5a6577', fontWeight: '600',
        fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em'
      }
    }
  },
  mounted() {
    let patentId = this.$store.state.patentId;
    if (patentId !== null) {
      axios.get(APPLICABILITY_URL + "?patid=" + patentId)
        .then((response) => { this.applicabilities = response.data.ipc; })
        .catch((e) => console.log(e));

      axios.get(THESISBYAPPLICANT_URL + "?patid=" + patentId)
        .then((response) => {
          this.authorThesises = response.data.thesis.hits.map(i => ({
            title: i._source['论文名称'],
            referenceNum: i._source['被引用次数'],
            source: i._source['来源'].join(', '),
            similarity: i._source['相似度']
          }));
        }).catch((e) => console.log(e));

      axios.get(SIMILARTHESIS_URL + "?patid=" + patentId)
        .then((response) => {
          this.otherThesises = response.data.hits.map(i => ({
            author: i._source['作者'].join('，'),
            title: i._source['论文名称'],
            referenceNum: i._source['被引用次数'],
            source: i._source['来源'].join(', '),
            similarity: i._source['相似度']
          }));
        }).catch((e) => console.log(e));
    }
  }
}
</script>

<style scoped>
.tech-detail {
  padding-bottom: var(--spacing-2xl);
}
.ipc-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}
.ipc-tag {
  display: inline-block;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-primary);
  background: var(--color-accent-light);
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid rgba(0, 102, 204, 0.12);
}
.badge-value {
  display: inline-block;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-primary);
  background: var(--color-accent-light);
  padding: 2px 10px;
  border-radius: 20px;
  font-family: var(--font-mono);
}
</style>
