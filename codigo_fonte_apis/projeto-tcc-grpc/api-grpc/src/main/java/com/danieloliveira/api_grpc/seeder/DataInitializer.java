package com.danieloliveira.api_grpc.seeder;


import com.danieloliveira.api_grpc.model.Product;
import com.danieloliveira.api_grpc.repository.ProductRepository;
import net.datafaker.Faker;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.Locale;
import java.util.Random;

@Component
public class DataInitializer implements CommandLineRunner {

    private final ProductRepository repository;

    public DataInitializer(ProductRepository repository) {
        this.repository = repository;
    }

    @Override
    public void run(String... args) throws Exception {
        long seed = 12345L;
        Faker faker = new Faker(new Locale("pt", "BR"), new Random(seed));

        int quantidadeDeProdutos = 10000;

        for (int i = 0; i < quantidadeDeProdutos; i++) {

            Product product = new Product();

            product.setName(faker.commerce().productName());
            product.setDescription(faker.lorem().sentence(10));
            product.setCategory(faker.commerce().department());
            product.setPrice(faker.number().randomDouble(2, 10, 5000));
            product.setStock(faker.number().numberBetween(1, 500));
            LocalDateTime base = LocalDateTime.of(2026, 1, 1, 0, 0);
            product.setCreatedAt(base.plusSeconds(i));


            repository.save(product);
        }

        System.out.println("Banco de dados populado. Os dados serão idênticos em toda inicialização.");
    }
}
