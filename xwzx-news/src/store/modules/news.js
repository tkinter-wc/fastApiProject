import { defineStore } from 'pinia'
import axios from 'axios'
import { apiConfig } from '../../config/api'

export const useNewsStore = defineStore('news', {
  state: () => ({
    newsList: [],
    newsDetail: {},
    categories: [],
    currentCategory: 1,
    loading: false,
    refreshing: false,
    finished: false,
    categoriesLoading: false,
    page: 1,
    fetching: false,
  }),
  
  actions: {
    // 获取新闻分类
    async getCategories() {
      if (this.categoriesLoading) return;
      
      this.categoriesLoading = true;
      
      try {
        // 调用API获取分类列表
        const response = await axios.get(`${apiConfig.baseURL}/api/news/categories`);
        
        if (response.data && response.data.code === 200) {
          // 设置分类数据
          this.categories = [...response.data.data, { id: 10, name: '更多' }];
          
          // 如果没有设置当前分类，则设置为第一个分类
          if (!this.currentCategory && this.categories.length > 0) {
            this.currentCategory = this.categories[0].id;
          }
        }
      } catch (error) {
        console.error('获取新闻分类失败:', error);
        // 设置默认分类，以防API请求失败
        this.categories = [
          { id: 1, name: '头条' },
          { id: 2, name: '社会' },
          { id: 3, name: '国内' },
          { id: 4, name: '国际' },
          { id: 5, name: '娱乐' },
          { id: 6, name: '体育' },
          { id: 7, name: '科技' }
        ];
      } finally {
        this.categoriesLoading = false;
      }
    },
    
    // 切换新闻分类
    changeCategory(categoryId) {
      if (this.currentCategory === categoryId && this.newsList.length) {
        return
      }
      this.currentCategory = categoryId
      this.newsList = []
      this.finished = false
      this.page = 1
      this.getNewsList(true)
    },
    
    // 获取新闻列表
    async getNewsList(isRefresh = false) {
      if (this.fetching) return
      if (this.finished && !isRefresh) {
        this.loading = false
        return
      }

      if (isRefresh) {
        this.refreshing = true
        this.newsList = []
        this.finished = false
        this.page = 1
      }

      this.fetching = true
      this.loading = true
      const page = this.page
      const pageSize = 10

      try {
        const params = {
          categoryId: this.currentCategory,
          page,
          pageSize
        }

        const response = await axios.get(`${apiConfig.baseURL}/api/news/list`, { params });

        if (response.data && response.data.code === 200) {
          const newsData = response.data.data.list || [];
          const hasMore = response.data.data.hasMore;

          if (isRefresh) {
            this.newsList = newsData;
          } else {
            const existIds = new Set(this.newsList.map(item => item.id));
            this.newsList = [
              ...this.newsList,
              ...newsData.filter(item => !existIds.has(item.id))
            ];
          }

          if (hasMore === false || newsData.length < pageSize) {
            this.finished = true;
          } else {
            this.page = page + 1;
          }
        }

      } catch (error) {
        console.error('获取新闻列表失败:', error)
      } finally {
        this.fetching = false
        this.loading = false
        this.refreshing = false
      }
    },
    
    // 获取新闻详情
    async getNewsDetail(id) {
      try {
        // 在开发环境中，使用模拟数据
        console.log('使用模拟新闻详情数据');
        

        // 实际项目中连接后端API的代码，取消注释即可使用
        const response = await axios.get(`${apiConfig.baseURL}/api/news/detail?id=${id}`);
        
        if (response.data && response.data.code === 200) {
          // 设置新闻详情数据
          this.newsDetail = response.data.data;
          return;
        } else {
          console.error('获取新闻详情失败: 接口返回错误');
          // 接口失败时使用模拟数据作为备选
        }

      } catch (error) {
        console.error('获取新闻详情失败:', error);
        // 接口失败时使用模拟数据作为备选
      } 
        // 查找已有列表中的新闻
//         const existingNews = this.newsList.find(item => item.id === Number(id))
        
//         if (existingNews) {
//           this.newsDetail = {
//             ...existingNews,
//             content: `这是${existingNews.title}的详细内容。这是一篇关于${this.getCategoryName(existingNews.categoryId)}的新闻报道，内容丰富详实。
            
// 新闻事件发生在最近，引起了广泛关注。多方消息人士透露，该事件的影响将持续一段时间。

// 专家表示，此类事件的出现有其必然性，也反映了当前社会的某些问题。我们应当理性看待，并从中吸取经验教训。

// 接下来，相关部门将会采取措施，确保类似事件不再发生。公众也应当提高警惕，增强自我保护意识。

// 这是新闻详情的第二段落，提供了更多背景信息和细节描述。

// 这是新闻详情的第三段落，包含了各方观点和评论。

// 这是新闻详情的最后一段，总结了事件的影响和未来展望。`,
//             relatedNews: Array.from({ length: 3 }, (_, i) => ({
//               id: 1000 + i,
//               title: `相关${this.getCategoryName(existingNews.categoryId)}新闻${i + 1}`,
//               image: `https://picsum.photos/id/${Math.floor(Math.random() * 100)}/200/200`
//             }))
//           }
//         } else {
//           // 如果列表中没有，则生成一个新的详情
//           const categoryId = this.currentCategory
//           this.newsDetail = {
//             id: Number(id),
//             title: `${this.getCategoryName(categoryId)}新闻${id}`,
//             description: `这是一条关于${this.getCategoryName(categoryId)}的新闻简介，包含了新闻的主要内容和亮点。`,
//             image: `https://picsum.photos/id/${Math.floor(Math.random() * 100)}/200/200`,
//             author: '新闻资讯',
//             publishTime: new Date().toLocaleString(),
//             categoryId: categoryId,
//             views: Math.floor(Math.random() * 10000),
//             content: `这是${this.getCategoryName(categoryId)}新闻${id}的详细内容。这是一篇关于${this.getCategoryName(categoryId)}的新闻报道，内容丰富详实。
            
// 新闻事件发生在最近，引起了广泛关注。多方消息人士透露，该事件的影响将持续一段时间。

// 专家表示，此类事件的出现有其必然性，也反映了当前社会的某些问题。我们应当理性看待，并从中吸取经验教训。

// 接下来，相关部门将会采取措施，确保类似事件不再发生。公众也应当提高警惕，增强自我保护意识。

// 这是新闻详情的第二段落，提供了更多背景信息和细节描述。

// 这是新闻详情的第三段落，包含了各方观点和评论。

// 这是新闻详情的最后一段，总结了事件的影响和未来展望。`,
//             relatedNews: Array.from({ length: 3 }, (_, i) => ({
//               id: 1000 + i,
//               title: `相关${this.getCategoryName(categoryId)}新闻${i + 1}`,
//               image: `https://picsum.photos/id/${Math.floor(Math.random() * 100)}/200/200`
//             }))
//           }
//         }
//             content: `这是${this.getCategoryName(categoryId)}新闻${id}的详细内容。这是一篇关于${this.getCategoryName(categoryId)}的新闻报道，内容丰富详实。
            
// 新闻事件发生在最近，引起了广泛关注。多方消息人士透露，该事件的影响将持续一段时间。

// 专家表示，此类事件的出现有其必然性，也反映了当前社会的某些问题。我们应当理性看待，并从中吸取经验教训。

// 接下来，相关部门将会采取措施，确保类似事件不再发生。公众也应当提高警惕，增强自我保护意识。

// 这是新闻详情的第二段落，提供了更多背景信息和细节描述。

// 这是新闻详情的第三段落，包含了各方观点和评论。

// 这是新闻详情的最后一段，总结了事件的影响和未来展望。`,
//             relatedNews: Array.from({ length: 3 }, (_, i) => ({
//               id: 1000 + i,
//               title: `相关${this.getCategoryName(categoryId)}新闻${i + 1}`,
//               image: `https://picsum.photos/id/${Math.floor(Math.random() * 100)}/200/200`
//             }))
//           }
//         }
//       } catch (error) {
//         console.error('获取新闻详情失败:', error)
//       }
//     },
    },
    // 获取分类名称
    getCategoryName(categoryId) {
      const category = this.categories.find(item => item.id === categoryId)
      return category ? category.name : '未知'
    }
  }
})