<template>
  <el-row>
    <el-col>
      <el-menu
        :default-active="activeIndex"
        class="Menu"
        mode="horizontal"
        router
        @select="handleSelect"
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#ffd04b"
      >
        <el-menu-item index="/movies">电影展厅</el-menu-item>
        <el-menu-item index="/mixup">混合模式</el-menu-item>
        <el-menu-item index="/fusion">融合模式</el-menu-item>
        <el-menu-item style="float:right;">
          <div v-if="this.$store.state.login" @click="tryLogout">
            {{this.$store.state.id}}
            <i
              class="el-icon-switch-button"
              style="color: #fff; position: relative; top: -2px"
            ></i>
          </div>
          <div v-else @click="tryLogin">
            登录
            <i class="el-icon-user" style="color: #fff;"></i>
          </div>
        </el-menu-item>
      </el-menu>
    </el-col>
    <el-dialog ref="dialog" title="登录" :visible.sync="this.$store.state.showDialog" width="30%" :before-close="handleClose"
    
    :modal="true"
    :modal-append-to-body="true">
      <span>
        <el-form 
        ref="loginForm" 
        status-icon
        :rules="loginRules"
        :model="loginForm" >
          <el-form-item label="账号" prop="id">
            <el-input clearable placeholder="登录功能施工中" v-model.number="loginForm.id"></el-input>
          </el-form-item>
          <el-form-item label="密码" prop="pwd">
            <el-input clearable v-model="loginForm.pwd" show-password></el-input>
          </el-form-item>
        </el-form>
      </span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="handleCancel">取 消</el-button>
        <el-button type="primary" @click="handleLogin">确 定</el-button>
      </span>
    </el-dialog>
    <el-dialog title="注销" :visible.sync="dialogVisible2" width="30%" :before-close="handleClose">
      <span>
        确认注销吗
      </span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible2 = false">取 消</el-button>
        <el-button type="primary" @click="handleLogout">确 定</el-button>
      </span>
    </el-dialog>
  </el-row>
</template>


<script>
export default {
  data() {
    return {
      activeIndex: "1",
      login: false,
      dialogVisible: false,
      dialogVisible2: false,
      loginForm: {
        id: "",
        pwd: null,
      },
      loginRules: {
        id: [            
          { required: true, message: '请输入账号', trigger: 'blur' },
        ],
        pwd: [            
          { required: true, message: '请输入密码', trigger: 'blur' }
        ],
      },
    };
  },
  methods: {
    handleSelect(key, keyPath) {
      console.log(key, keyPath);
    },
    handleCancel(){
      this.$store.dispatch('change');
    },
    tryLogout() {
      this.dialogVisible2 = true;
    },   
    handleLogout() {
      this.dialogVisible2 = false;
      this.$store.dispatch('changeOut');
    },
    tryLogin() {
      // this.dialogVisible = true;       
      this.$store.dispatch('change')      
    },
    handleLogin() {
      let _this = this;
      this.$axios.login(this.loginForm.id).then(
        response => {
          // 成功回调
          var res = response.data;
          console.log(res);
          if (res.data.res == true) {
            _this.$message({ message: "登录成功", type: "success" });
            _this.$store.dispatch('changeId', this.loginForm.id);
            _this.$store.dispatch('changeIn');  
            // this.dialogVisible = false;
            _this.$store.dispatch('change')
          } else {
            console.log("null");
            _this.$message("学号不存在或密码错误");
          }
        },
        response => {
          // 错误回调
          this.$message.error("失败，请查看网络是否正常");
        }
      );
    }, 
    
    handleClose(done) {
      var _this = this;
      this.$confirm('确认关闭？')
        .then(_ => {
          done();
          _this.handleCancel();
        })
        .catch(_ => {});
    }
  }
};
</script>
