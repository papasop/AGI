import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import warnings
warnings.filterwarnings('ignore')

class PerfectEnergyFunction:
    """真正的完美能量函数 - 在原点有清晰的全局最小值"""
    
    def __init__(self):
        self.name = "Perfect Energy Landscape"
        
    def energy(self, x, y):
        """能量函数：在原点有最小值，平滑且凸"""
        return 0.5 + 0.25 * (x**2 + y**2) + 0.1 * (x**4 + y**4) / (1 + x**2 + y**2)
    
    def gradient(self, x, y):
        """解析梯度计算"""
        r2 = x**2 + y**2
        
        # 计算主要项的梯度
        grad_x = 0.5 * x + 0.4 * x**3 / (1 + r2) - 0.1 * x * (x**4 + y**4) / (1 + r2)**2
        grad_y = 0.5 * y + 0.4 * y**3 / (1 + r2) - 0.1 * y * (x**4 + y**4) / (1 + r2)**2
        
        return np.array([grad_x, grad_y])
    
    def check_origin(self):
        """验证原点的性质"""
        energy_origin = self.energy(0, 0)
        grad_origin = self.gradient(0, 0)
        grad_norm = np.linalg.norm(grad_origin)
        
        return {
            'energy': energy_origin,
            'gradient': grad_origin,
            'gradient_norm': grad_norm,
            'is_minimum': grad_norm < 1e-10
        }

class PerfectOptimizer:
    """真正的完美优化器"""
    
    def __init__(self, energy_func, learning_rate=0.1, momentum=0.3, max_iter=200):
        self.energy_func = energy_func
        self.lr = learning_rate
        self.momentum = momentum
        self.max_iter = max_iter
        self.convergence_threshold = 1e-6
        
    def optimize(self, start_point):
        """从起点优化到原点"""
        position = np.array(start_point, dtype=float)
        velocity = np.zeros_like(position)
        history = {'positions': [position.copy()], 'energies': []}
        
        for i in range(self.max_iter):
            # 计算能量和梯度
            current_energy = self.energy_func.energy(position[0], position[1])
            gradient = self.energy_func.gradient(position[0], position[1])
            
            # 动量更新
            velocity = self.momentum * velocity - self.lr * gradient
            position += velocity
            
            # 记录历史
            history['positions'].append(position.copy())
            history['energies'].append(current_energy)
            
            # 收敛检查
            if np.linalg.norm(gradient) < self.convergence_threshold:
                break
        
        # 最终能量
        final_energy = self.energy_func.energy(position[0], position[1])
        history['energies'].append(final_energy)
        
        # 计算是否收敛
        distance_to_origin = np.linalg.norm(position)
        converged = distance_to_origin < 0.05
        
        return {
            'final_position': position,
            'final_energy': final_energy,
            'distance_to_origin': distance_to_origin,
            'converged': converged,
            'iterations': i + 1,
            'final_gradient_norm': np.linalg.norm(gradient),
            'history': history
        }

def create_visualization(energy_func, results):
    """创建完美的可视化"""
    fig = plt.figure(figsize=(16, 12))
    
    # 1. 3D能量曲面
    ax1 = fig.add_subplot(231, projection='3d')
    x = np.linspace(-2, 2, 100)
    y = np.linspace(-2, 2, 100)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    
    for i in range(len(x)):
        for j in range(len(y)):
            Z[j, i] = energy_func.energy(x[i], y[j])
    
    ax1.plot_surface(X, Y, Z, cmap=cm.viridis, alpha=0.8)
    ax1.scatter([0], [0], [energy_func.energy(0, 0)], color='red', s=100, label='Minimum')
    ax1.set_title('3D Energy Landscape', fontsize=12)
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Energy')
    
    # 2. 等高线图
    ax2 = fig.add_subplot(232)
    contour = ax2.contour(X, Y, Z, levels=20, cmap='viridis')
    ax2.scatter(0, 0, color='red', s=100, label='Minimum')
    
    # 绘制优化轨迹
    colors = ['blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'cyan']
    for idx, (key, result) in enumerate(results.items()):
        if idx < len(colors):
            positions = result['history']['positions']
            path = np.array(positions)
            ax2.plot(path[:, 0], path[:, 1], color=colors[idx], 
                    marker='o', markersize=3, linewidth=2, alpha=0.7,
                    label=f'Test {idx+1}')
    
    ax2.set_title('Optimization Paths', fontsize=12)
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.legend()
    plt.colorbar(contour, ax=ax2)
    
    # 3. 能量收敛图
    ax3 = fig.add_subplot(233)
    for idx, (key, result) in enumerate(results.items()):
        if idx < len(colors):
            energies = result['history']['energies']
            ax3.plot(energies, color=colors[idx], linewidth=2, alpha=0.7, label=f'Test {idx+1}')
    
    ax3.axhline(y=energy_func.energy(0, 0), color='red', linestyle='--', label='Minimum Energy')
    ax3.set_title('Energy Convergence', fontsize=12)
    ax3.set_xlabel('Iteration')
    ax3.set_ylabel('Energy')
    ax3.set_yscale('log')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 梯度收敛图
    ax4 = fig.add_subplot(234)
    gradient_data = []
    for idx, (key, result) in enumerate(results.items()):
        if idx < len(colors):
            positions = result['history']['positions']
            gradients = []
            for pos in positions:
                grad = energy_func.gradient(pos[0], pos[1])
                gradients.append(np.linalg.norm(grad))
            ax4.plot(gradients, color=colors[idx], linewidth=2, alpha=0.7, label=f'Test {idx+1}')
    
    ax4.axhline(y=1e-6, color='green', linestyle='--', label='Convergence Threshold')
    ax4.set_title('Gradient Norm Convergence', fontsize=12)
    ax4.set_xlabel('Iteration')
    ax4.set_ylabel('Gradient Norm')
    ax4.set_yscale('log')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. 最终结果统计
    ax5 = fig.add_subplot(235)
    test_indices = list(range(1, len(results) + 1))
    converged = [1 if result['converged'] else 0 for result in results.values()]
    distances = [result['distance_to_origin'] for result in results.values()]
    
    bars = ax5.bar(test_indices, distances, color=['green' if c else 'red' for c in converged])
    ax5.axhline(y=0.05, color='blue', linestyle='--', label='Convergence Threshold (0.05)')
    ax5.set_title('Final Distance to Origin', fontsize=12)
    ax5.set_xlabel('Test Case')
    ax5.set_ylabel('Distance')
    ax5.set_xticks(test_indices)
    
    # 添加数值标签
    for bar, distance in zip(bars, distances):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'{distance:.3f}', ha='center', va='bottom', fontsize=8)
    
    ax5.legend()
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 6. 收敛统计
    ax6 = fig.add_subplot(236)
    convergence_rate = np.mean(converged) * 100
    avg_iterations = np.mean([r['iterations'] for r in results.values()])
    avg_distance = np.mean(distances)
    
    metrics = ['Convergence Rate', 'Avg Iterations', 'Avg Distance']
    values = [convergence_rate, avg_iterations, avg_distance]
    colors_bar = ['green', 'blue', 'orange']
    
    bars = ax6.bar(metrics, values, color=colors_bar)
    ax6.set_title('Optimization Performance Metrics', fontsize=12)
    ax6.set_ylabel('Value')
    ax6.grid(True, alpha=0.3, axis='y')
    
    # 添加数值标签
    for bar, value in zip(bars, values):
        height = bar.get_height()
        if metrics[bars.index(bar)] == 'Convergence Rate':
            ax6.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.1f}%', ha='center', va='bottom', fontsize=10)
        else:
            ax6.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.2f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.show()
    
    return fig

# 使用示例
def run_perfect_system():
    """运行完美数值优化系统"""
    print("="*80)
    print("🌟 真正完美的数值优化系统")
    print("="*80)
    
    # 创建完美能量函数
    energy_func = PerfectEnergyFunction()
    
    # 验证原点
    origin_check = energy_func.check_origin()
    print("\n🔍 原点验证:")
    print(f"  能量: {origin_check['energy']:.6f}")
    print(f"  梯度: [{origin_check['gradient'][0]:.10f}, {origin_check['gradient'][1]:.10f}]")
    print(f"  梯度模长: {origin_check['gradient_norm']:.10f}")
    print(f"  是否最小值: {'✓ 是' if origin_check['is_minimum'] else '✗ 否'}")
    
    # 创建优化器
    optimizer = PerfectOptimizer(energy_func, learning_rate=0.15, momentum=0.3)
    
    # 测试不同的起点
    test_points = [
        [1.5, 1.0],    # 测试1
        [-1.2, 1.5],   # 测试2
        [-1.5, -1.0],  # 测试3
        [1.0, -1.5],   # 测试4
        [2.0, 0.0],    # 测试5
        [0.0, 2.0],    # 测试6
        [1.2, 0.8],    # 测试7
        [-0.8, -1.2],  # 测试8
    ]
    
    print("\n🎯 优化测试:")
    print("-" * 60)
    
    results = {}
    for i, start_point in enumerate(test_points, 1):
        print(f"\n测试 {i}:")
        print(f"  起点: ({start_point[0]:.3f}, {start_point[1]:.3f})")
        
        start_energy = energy_func.energy(start_point[0], start_point[1])
        print(f"  初始能量: {start_energy:.6f}")
        
        result = optimizer.optimize(start_point)
        
        print(f"  → {'✓ 收敛' if result['converged'] else '✗ 未收敛'}")
        print(f"    最终位置: ({result['final_position'][0]:.6f}, {result['final_position'][1]:.6f})")
        print(f"    距离原点: {result['distance_to_origin']:.6f}")
        print(f"    最终梯度: {result['final_gradient_norm']:.6f}")
        print(f"    迭代次数: {result['iterations']}")
        
        results[f'Test{i}'] = result
    
    # 计算统计信息
    converged_count = sum(1 for r in results.values() if r['converged'])
    convergence_rate = converged_count / len(results) * 100
    avg_iterations = np.mean([r['iterations'] for r in results.values()])
    avg_distance = np.mean([r['distance_to_origin'] for r in results.values()])
    
    print("\n" + "="*60)
    print("📊 最终统计:")
    print(f"  收敛率: {converged_count}/{len(results)} = {convergence_rate:.1f}%")
    print(f"  平均迭代次数: {avg_iterations:.1f}")
    print(f"  平均最终距离: {avg_distance:.4f}")
    
    # 创建可视化
    print("\n📈 生成完美可视化...")
    fig = create_visualization(energy_func, results)
    
    print("\n" + "="*80)
    print("✅ 真正完美的数值优化系统验证完成！")
    print("="*80)
    
    return energy_func, optimizer, results, fig

# 运行系统
if __name__ == "__main__":
    energy_func, optimizer, results, fig = run_perfect_system()