<template>
  <div class="pagination">
    <button 
      @click="onPageChange(currentPage - 1)" 
      class="page-btn prev" 
      :disabled="currentPage === 1"
    >
      上一页
    </button>
    
    <div class="page-numbers">
      <template v-for="page in displayedPages" :key="page">
        <button 
          v-if="page !== '...'" 
          @click="onPageChange(page)" 
          class="page-number" 
          :class="{ active: page === currentPage }"
        >
          {{ page }}
        </button>
        <span v-else class="ellipsis">...</span>
      </template>
    </div>
    
    <button 
      @click="onPageChange(currentPage + 1)" 
      class="page-btn next" 
      :disabled="currentPage === totalPages"
    >
      下一页
    </button>
    
    <div class="page-size">
      <select v-model="localPageSize" @change="onPageSizeChange">
        <option :value="5">5条/页</option>
        <option :value="10">10条/页</option>
        <option :value="20">20条/页</option>
        <option :value="50">50条/页</option>
      </select>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TaskPagination',
  props: {
    currentPage: {
      type: Number,
      required: true
    },
    totalPages: {
      type: Number,
      required: true
    },
    pageSize: {
      type: Number,
      default: 10
    }
  },
  data() {
    return {
      localPageSize: this.pageSize
    };
  },
  computed: {
    displayedPages() {
      const pages = [];
      const totalVisiblePages = 7;
      
      if (this.totalPages <= totalVisiblePages) {
        // 如果总页数小于可见页数，显示所有页码
        for (let i = 1; i <= this.totalPages; i++) {
          pages.push(i);
        }
      } else {
        // 总是显示第一页
        pages.push(1);
        
        // 确定起始页和结束页
        let startPage = Math.max(2, this.currentPage - 1);
        let endPage = Math.min(this.totalPages - 1, this.currentPage + 1);
        
        // 调整起始页和结束页以显示5个页码
        if (startPage === 2) {
          endPage = Math.min(this.totalPages - 1, 5);
        } else if (endPage === this.totalPages - 1) {
          startPage = Math.max(2, this.totalPages - 4);
        }
        
        // 添加省略号(如果需要的话)
        if (startPage > 2) {
          pages.push('...');
        }
        
        // 添加中间页码
        for (let i = startPage; i <= endPage; i++) {
          pages.push(i);
        }
        
        // 添加省略号(如果需要的话)
        if (endPage < this.totalPages - 1) {
          pages.push('...');
        }
        
        // 总是显示最后一页
        pages.push(this.totalPages);
      }
      
      return pages;
    }
  },
  methods: {
    onPageChange(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.$emit('page-change', page);
      }
    },
    onPageSizeChange() {
      this.$emit('page-size-change', this.localPageSize);
    }
  }
};
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 20px 0;
  flex-wrap: wrap;
  gap: 10px;
}

.page-numbers {
  display: flex;
  align-items: center;
}

.page-btn, .page-number {
  padding: 6px 12px;
  margin: 0 4px;
  border: 1px solid #d9d9d9;
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:disabled {
  color: #d9d9d9;
  cursor: not-allowed;
}

.page-number {
  min-width: 32px;
  text-align: center;
}

.page-number.active {
  background-color: #1890ff;
  color: white;
  border-color: #1890ff;
}

.ellipsis {
  margin: 0 8px;
}

.page-size {
  margin-left: 16px;
}

.page-size select {
  padding: 6px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}

@media (max-width: 576px) {
  .pagination {
    flex-direction: column;
    gap: 15px;
  }
  
  .page-size {
    margin-left: 0;
  }
}
</style>
