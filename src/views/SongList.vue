<template>
  <div>
    <!-- 组件内容 -->
  </div>
</template>

<script>
export default {
  data() {
    return {
      showDialog: false,
      message: ''
    };
  },
  methods: {
    someFunction() {
      if (!this.showDialog) {
        this.openDialog("确定要继续连接吗?");
      }
    },
    openDialog(message) {
      this.message = message;
      this.showDialog = true;
    },
    handleYes() {
      this.showDialog = false;
      // 执行“是”的操作
    },
    handleNo() {
      this.showDialog = false;
      // 执行“否”的操作
    }
  }
};
</script>

<style scoped>
.dialog {
}
</style>
