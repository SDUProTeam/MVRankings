<template>
  <div class="mixup">
    <el-col>
      <el-row :span="6" style="padding-left: 64px; padding-right: 64px">
        <el-form
          ref="form"
          :model="form"
          :inline="true"
          status-icon
          :rules="rules"
          size="medium"
        >
            <el-form-item label="电影名">
              <el-input clearable v-model="form.name" style="width: 250px"></el-input>
            </el-form-item>
            <el-form-item label="评分">
              <el-col :span="9">
                <el-form-item>
                  <el-input oninput="value=value.replace(/[^0-9.]/g,'')" v-model="form.rate_min" placeholder="0" maxlength=3 text-align='center' style="width: 55px; text-align: center;"></el-input>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                —
              </el-col>
              <el-col :span="9">
                <el-form-item>
                  <el-input oninput="value=value.replace(/[^0-9.]/g,'')" v-model="form.rate_max" placeholder="10" maxlength=3 style="width: 55px; text-align: center"></el-input>
                </el-form-item>
              </el-col>
            </el-form-item>
            <el-form-item class="form-item" label="上映年份">
              <el-col :span="9">
                <el-form-item>
                  <el-input v-model.number="form.time_min" maxlength=4 text-align='center' style="width: 70px; text-align: center;"></el-input>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                —
              </el-col>
              <el-col :span="9">
                <el-form-item>
                  <el-input v-model.number="form.time_max" maxlength=4 style="width: 70px; text-align: center"></el-input>
                </el-form-item>
              </el-col>
            </el-form-item>
            <el-form-item label="主演">
              <el-input clearable v-model="form.casts" style="width: 100px"></el-input>
            </el-form-item>
            <el-form-item label="导演">
              <el-input clearable v-model="form.directors" style="width: 100px"></el-input>
            </el-form-item>
            <el-form-item label="来源">
              <el-select v-model="form.source" clearable placeholder="所有来源" style="width: 130px">
                <el-option
                  v-for="item in options"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value">
                </el-option>
              </el-select>
            </el-form-item>
            <el-form-item>          
              <el-button
                type="primary"
                :loading="qloading"
                @click="get"
              >查询</el-button>
            </el-form-item>
        </el-form>
      </el-row>
      <el-row style="padding-left: 48px; padding-right: 48px">
        <el-table
          ref="table"
          :data="tableData"
          style="width: 100%;"
          @sort-change="sortChange"
        >
          <el-table-column label="海报" prop="name" width=50>
            <template slot-scope="scope">
              <el-popover placement="bottom-end" title="" trigger="hover">
                <el-image :src="scope.row.cover"  style="height: 360px;width: 360px" fit="contain"/>
                <el-image slot="reference" :src="scope.row.cover" :alt="scope.row.cover" style="height: 50px;width: 50px" fit="contain"/>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column 
          v-for="(v,i) in columns" 
          :key='i' 
          :prop="v.field" 
          :label="v.title" 
          :width="v.width"
          :sortable="v.sortable">
              <template slot-scope="scope">
                  <span>{{scope.row[v.field]}}</span>
              </template>
          </el-table-column>
          <el-table-column label="来源" prop="source" width=100>
            <template slot-scope="scope">
              <el-link :href="scope.row.url" type="primary">{{scope.row.source}}</el-link>
            </template>
          </el-table-column>
        </el-table>
        <div style="text-align: center; margin-top: 4px;">
          <el-pagination
            :hide-on-single-page="value"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page.sync="currentPage"
            layout="total, prev, pager, next, jumper"
            :total="totalItems"
          ></el-pagination>
        </div>
      </el-row>
    </el-col>
  </div>
</template>

<script>
export default {
  mounted() {
    this.get()
  }, 
  data() {
    return {
      oldRowJson: null,     
      columns: [
          { field: "name", title: "电影名", width: 240 },
          { field: "rate", title: "评分", width: 80, sortable: 'custom' },
          { field: "time", title: "上映时间", width: 100, sortable: 'custom' },
          { field: "type", title: "类型", width: 160 },
          { field: "casts", title: "主演", width: 360 }, 
          { field: "directors", title: "导演", width: 300 },
      ],
      options: [
        { value: "douban", label: "豆瓣" }, 
        { value: "maoyan", label: "猫眼" }, 
        { value: "mtime", label: "时光网" }, 
      ], 
      ploading: false,
      qloading: false,
      currentPage: 1,
      pagesize: 10,
      totalItems: 0,
      form: {
        name: null,
        rate_min: null,
        rate_max: null,
        time_min: null,
        time_max: null,
        directors: null,
        casts: null,
        order: null,
      },
      rules: {
      },
      tableData: [],
      fileList: [],
      srcDict: {
        douban: "豆瓣", 
        mtime: "时光网", 
        maoyan: "猫眼"
      }
    };
  },
  methods: {
    get() {
      let _this = this;
      _this.qloading = true;
      _this.form['offset'] = this.currentPage * this.pagesize - this.pagesize;
      if(_this.form['source'] == "")
        delete _this.form['source'];
      this.$axios.search(_this.form).then(
        response => {
          // 成功回调
          var data = response.data.data;
          _this.totalItems = response.data.total;
          _this.qloading = false;
          console.log(data);
          if (data != null) {
            data.map(i =>{
              i.source = _this.srcDict[i.source];
              let lst = ["casts", "directors", "type"];
              lst.forEach((param)=>{
                if(param in i)
                  i[param] = i[param].join("／");
              });
              return i;
            });
            _this.tableData = data;
            this.$message({ message: "查询成功", type: "success" });
          } else {
            console.log("null");
            this.$message("没有查询到相关结果");
            _this.tableData = [];
          }
        },
        response => {
          // 错误回调
          var result = response;
          this.$message.error("查询失败，请查看网络是否正常");
          _this.qloading = false;
          _this.tableData = [];
          _this.totalItems = 0;
        }
      );
    },

    onSuccess(response, file, fileList) {
      console.log(response);
      if (response.data.res == true) {
        this.$message({ message: response.msg, type: "success" });
      } else {
        this.$message.error(response.msg);
      }
    },
    
    handleCurrentChange(currentPage) {
      this.currentPage = currentPage;
      this.get()
    }, //组件自带监控当前页码

    handleSizeChange(curSize) {
      this.pagesize = curSize;
    },

    sortChange(args) {
      if(args.order=="ascending"){
        this.form["order"] = args.prop;
      } else {
        this.form["order"] = "-" + args.prop;
      }
      this.get();
    },
  }
};
</script>

<style>
*{
  text-align: center
}
/* .tb-edit .el-input {
    display: none
}
.tb-edit .current-row .el-input {
    display: block
}
.tb-edit .current-row .el-input+span {
    display: none
} */
</style>


